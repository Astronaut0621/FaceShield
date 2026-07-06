from __future__ import annotations

import argparse
import csv
import io
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
import paddle
import paddle.nn.functional as F

from dataset import compute_frequency_tensor, pil_to_rgb_tensor, read_manifest, split_rows
from metrics import classification_metrics
from models import build_model, is_fusion_model


DEFAULT_MODEL_DIRS = [
    Path("model/deploy/baseline"),
    Path("model/deploy/fusion_v2"),
    Path("model/deploy/fusion_v3"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate FaceShield models under in-memory JPEG compression."
    )
    parser.add_argument("--data-root", type=Path, default=Path("data/ffpp_faces"))
    parser.add_argument("--manifest", type=Path, default=Path("face_manifest_clean.csv"))
    parser.add_argument(
        "--model-dir",
        type=Path,
        action="append",
        default=None,
        help="Directory containing config.json and best.pdparams. Can be provided multiple times.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("model/robustness/jpeg"))
    parser.add_argument("--qualities", type=int, nargs="+", default=[95, 75, 50, 30])
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", choices=["gpu", "cpu"], default="cpu")
    parser.add_argument("--limit", type=int, default=None, help="Optional quick-test limit per split.")
    parser.add_argument("--no-original", action="store_true", help="Skip original uncompressed images.")
    return parser.parse_args()


def resolve_manifest_path(data_root: Path, manifest: Path) -> Path:
    if manifest.is_absolute():
        return manifest
    candidate = data_root / manifest
    if candidate.exists():
        return candidate
    return manifest


def load_config(model_dir: Path) -> dict:
    config_path = model_dir / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config.json: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def available_model_dirs(model_dirs: list[Path] | None) -> list[Path]:
    candidates = model_dirs if model_dirs else DEFAULT_MODEL_DIRS
    existing = []
    for model_dir in candidates:
        if (model_dir / "config.json").exists() and (model_dir / "best.pdparams").exists():
            existing.append(model_dir)
    return existing


def jpeg_reencode(image: Image.Image, quality: int) -> Image.Image:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def prepare_image(image_path: Path, image_size: int, jpeg_quality: int | None) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    if image.size != (image_size, image_size):
        image = image.resize((image_size, image_size), Image.BILINEAR)
    if jpeg_quality is not None:
        image = jpeg_reencode(image, jpeg_quality)
    return image


def iter_batches(items: list[dict[str, str]], batch_size: int):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def evaluate_model_quality(
    model: paddle.nn.Layer,
    model_name: str,
    rows: list[dict[str, str]],
    data_root: Path,
    image_size: int,
    batch_size: int,
    jpeg_quality: int | None,
) -> tuple[dict[str, float], list[dict[str, object]]]:
    y_true: list[int] = []
    y_prob: list[float] = []
    predictions: list[dict[str, object]] = []
    total_loss = 0.0
    total_count = 0

    with paddle.no_grad():
        for batch_rows in iter_batches(rows, batch_size):
            images = [
                prepare_image(data_root / row["face_image_path"], image_size, jpeg_quality)
                for row in batch_rows
            ]
            rgb = np.stack([pil_to_rgb_tensor(image) for image in images]).astype("float32")
            rgb_tensor = paddle.to_tensor(rgb)
            labels = np.array([int(row["label"]) for row in batch_rows], dtype="int64")
            label_tensor = paddle.to_tensor(labels)

            if is_fusion_model(model_name):
                frequency = np.stack(
                    [compute_frequency_tensor(image, model_name) for image in images]
                ).astype("float32")
                logits = model(rgb_tensor, paddle.to_tensor(frequency))
            else:
                logits = model(rgb_tensor)

            batch_loss = F.cross_entropy(logits, label_tensor, reduction="sum")
            prob = F.softmax(logits, axis=1).numpy()[:, 1]

            total_loss += float(batch_loss.numpy())
            total_count += len(batch_rows)
            y_true.extend(labels.tolist())
            y_prob.extend(prob.astype("float64").tolist())

            for row, fake_prob in zip(batch_rows, prob):
                fake_probability = float(fake_prob)
                predictions.append(
                    {
                        "split": row["split"],
                        "label": int(row["label"]),
                        "label_name": row["label_name"],
                        "method": row["method"],
                        "video_stem": row["video_stem"],
                        "face_image_path": row["face_image_path"],
                        "fake_probability": fake_probability,
                        "predicted_label": int(fake_probability >= 0.5),
                    }
                )

    metrics = classification_metrics(y_true, y_prob)
    metrics["loss"] = total_loss / total_count if total_count else 0.0
    metrics["samples"] = float(total_count)
    return metrics, predictions


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_metric(value: object) -> str:
    if isinstance(value, (int, np.integer)):
        return str(value)
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.4f}"
    return str(value)


def write_summary_markdown(path: Path, metric_rows: list[dict[str, object]]) -> None:
    headers = [
        "model",
        "quality",
        "accuracy",
        "auc",
        "precision",
        "recall",
        "f1",
        "loss",
        "auc_drop",
        "f1_drop",
    ]
    lines = [
        "# JPEG 压缩鲁棒性测试",
        "",
        "测试方式：对 test split 的人脸裁剪图在内存中进行 JPEG 重新编码，评估同一模型在不同压缩质量下的指标变化；原始图片不被修改。",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(headers) - 1)) + " |",
    ]
    for row in metric_rows:
        lines.append("| " + " | ".join(format_metric(row.get(header, "")) for header in headers) + " |")
    lines.append("")
    lines.append("说明：`auc_drop` 和 `f1_drop` 以同一模型的 original 结果为基准，数值越大表示压缩后下降越明显。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.device == "gpu" and paddle.device.is_compiled_with_cuda():
        paddle.set_device("gpu")
    else:
        paddle.set_device("cpu")

    model_dirs = available_model_dirs(args.model_dir)
    if not model_dirs:
        raise SystemExit("No valid model directories found. Expected config.json and best.pdparams.")

    manifest_path = resolve_manifest_path(args.data_root, args.manifest)
    rows = split_rows(read_manifest(manifest_path), "test")
    if args.limit is not None:
        rows = rows[: args.limit]

    qualities: list[int | None] = []
    if not args.no_original:
        qualities.append(None)
    qualities.extend(args.qualities)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metric_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    started_at = time.time()

    for model_dir in model_dirs:
        config = load_config(model_dir)
        model_name = str(config.get("model") or model_dir.name)
        image_size = int(config.get("image_size", 224))
        dropout = float(config.get("dropout", 0.3))
        feature_dim = int(config.get("feature_dim", 128))

        model = build_model(model_name, dropout=dropout, feature_dim=feature_dim)
        model.set_state_dict(paddle.load(str(model_dir / "best.pdparams")))
        model.eval()

        baseline_metrics: dict[str, float] | None = None
        for quality in qualities:
            quality_label = "original" if quality is None else f"jpeg_q{quality}"
            print(f"evaluating model={model_name} quality={quality_label} samples={len(rows)}", flush=True)
            metrics, predictions = evaluate_model_quality(
                model=model,
                model_name=model_name,
                rows=rows,
                data_root=args.data_root,
                image_size=image_size,
                batch_size=args.batch_size,
                jpeg_quality=quality,
            )
            if quality is None:
                baseline_metrics = metrics
            auc_drop = (
                float(baseline_metrics["auc"]) - float(metrics["auc"])
                if baseline_metrics is not None
                else 0.0
            )
            f1_drop = (
                float(baseline_metrics["f1"]) - float(metrics["f1"])
                if baseline_metrics is not None
                else 0.0
            )
            metric_row = {
                "model": model_name,
                "model_dir": str(model_dir),
                "quality": quality_label,
                "samples": int(metrics["samples"]),
                "accuracy": metrics["accuracy"],
                "auc": metrics["auc"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "loss": metrics["loss"],
                "auc_drop": auc_drop,
                "f1_drop": f1_drop,
            }
            metric_rows.append(metric_row)
            for prediction in predictions:
                prediction_rows.append(
                    {
                        "model": model_name,
                        "quality": quality_label,
                        **prediction,
                    }
                )

    elapsed = time.time() - started_at
    result = {
        "manifest": str(manifest_path),
        "data_root": str(args.data_root),
        "split": "test",
        "qualities": ["original" if quality is None else quality for quality in qualities],
        "model_dirs": [str(path) for path in model_dirs],
        "elapsed_seconds": round(elapsed, 2),
        "metrics": metric_rows,
    }

    (args.output_dir / "metrics_by_quality.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_csv(
        args.output_dir / "metrics_by_quality.csv",
        metric_rows,
        [
            "model",
            "model_dir",
            "quality",
            "samples",
            "accuracy",
            "auc",
            "precision",
            "recall",
            "f1",
            "loss",
            "auc_drop",
            "f1_drop",
        ],
    )
    write_csv(
        args.output_dir / "predictions_by_quality.csv",
        prediction_rows,
        [
            "model",
            "quality",
            "split",
            "label",
            "label_name",
            "method",
            "video_stem",
            "face_image_path",
            "fake_probability",
            "predicted_label",
        ],
    )
    write_summary_markdown(args.output_dir / "summary.md", metric_rows)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
