from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
import paddle
import paddle.nn.functional as F

from dataset import compute_frequency_tensor, pil_to_rgb_tensor, read_manifest
from metrics import classification_metrics
from models import build_model, is_fusion_model


DEFAULT_MODEL_DIRS = [
    Path("model/deploy/fusion_v2"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate deployed FaceShield models on a new manipulation type or dataset."
    )
    parser.add_argument("--data-root", type=Path, default=Path("data/ffpp_faces_faceswap"))
    parser.add_argument("--manifest", type=Path, default=Path("face_manifest.csv"))
    parser.add_argument(
        "--model-dir",
        type=Path,
        action="append",
        default=None,
        help="Directory containing config.json and best.pdparams. Can be provided multiple times.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("model/cross_domain"))
    parser.add_argument("--domain-name", default=None, help="Reader-facing domain name for reports.")
    parser.add_argument("--split", default="test", choices=["train", "val", "test", "all"])
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", choices=["gpu", "cpu"], default="cpu")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--limit", type=int, default=None, help="Optional quick-test row limit.")
    parser.add_argument(
        "--exclude-fallback",
        action="store_true",
        help="Skip face crops produced by center-crop fallback when no face was detected.",
    )
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
    existing: list[Path] = []
    for model_dir in candidates:
        if (model_dir / "config.json").exists() and (model_dir / "best.pdparams").exists():
            existing.append(model_dir)
    return existing


def infer_domain_name(rows: list[dict[str, str]], output_dir: Path) -> str:
    fake_methods = sorted(
        {
            row.get("method", "")
            for row in rows
            if row.get("label") == "1" and row.get("method")
        }
    )
    if fake_methods:
        return "+".join(fake_methods)
    return output_dir.name


def filter_rows(
    rows: list[dict[str, str]],
    data_root: Path,
    split: str,
    exclude_fallback: bool,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    kept: list[dict[str, str]] = []
    skipped = {
        "split": 0,
        "error": 0,
        "fallback": 0,
        "missing_face_image_path": 0,
        "missing_file": 0,
    }
    for row in rows:
        if split != "all" and row.get("split") != split:
            skipped["split"] += 1
            continue
        if row.get("error"):
            skipped["error"] += 1
            continue
        if exclude_fallback and row.get("fallback") == "1":
            skipped["fallback"] += 1
            continue
        face_image_path = row.get("face_image_path")
        if not face_image_path:
            skipped["missing_face_image_path"] += 1
            continue
        if not (data_root / face_image_path).exists():
            skipped["missing_file"] += 1
            continue
        kept.append(row)
    return kept, skipped


def prepare_image(image_path: Path, image_size: int) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    if image.size != (image_size, image_size):
        image = image.resize((image_size, image_size), Image.BILINEAR)
    return image


def iter_batches(items: list[dict[str, str]], batch_size: int):
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def confusion_counts(y_true: list[int], y_prob: list[float], threshold: float) -> dict[str, int]:
    y_true_arr = np.asarray(y_true, dtype="int64")
    y_pred_arr = (np.asarray(y_prob, dtype="float64") >= threshold).astype("int64")
    return {
        "tp": int(((y_pred_arr == 1) & (y_true_arr == 1)).sum()),
        "fp": int(((y_pred_arr == 1) & (y_true_arr == 0)).sum()),
        "tn": int(((y_pred_arr == 0) & (y_true_arr == 0)).sum()),
        "fn": int(((y_pred_arr == 0) & (y_true_arr == 1)).sum()),
    }


def evaluate_model(
    model: paddle.nn.Layer,
    model_name: str,
    rows: list[dict[str, str]],
    data_root: Path,
    image_size: int,
    batch_size: int,
    threshold: float,
) -> tuple[dict[str, float], list[dict[str, object]]]:
    y_true: list[int] = []
    y_prob: list[float] = []
    predictions: list[dict[str, object]] = []
    total_loss = 0.0
    total_count = 0

    with paddle.no_grad():
        for batch_rows in iter_batches(rows, batch_size):
            images = [
                prepare_image(data_root / row["face_image_path"], image_size)
                for row in batch_rows
            ]
            rgb = np.stack([pil_to_rgb_tensor(image) for image in images]).astype("float32")
            labels = np.array([int(row["label"]) for row in batch_rows], dtype="int64")
            rgb_tensor = paddle.to_tensor(rgb)
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
                predicted_label = int(fake_probability >= threshold)
                label = int(row["label"])
                predictions.append(
                    {
                        "split": row.get("split", ""),
                        "label": label,
                        "label_name": row.get("label_name", "fake" if label else "real"),
                        "method": row.get("method", ""),
                        "video_stem": row.get("video_stem", ""),
                        "face_image_path": row["face_image_path"],
                        "source_frame_path": row.get("source_frame_path", ""),
                        "source_video": row.get("source_video", ""),
                        "fallback": row.get("fallback", ""),
                        "fake_probability": fake_probability,
                        "predicted_label": predicted_label,
                        "predicted_name": "fake" if predicted_label else "real",
                        "correct": int(predicted_label == label),
                    }
                )

    metrics = classification_metrics(y_true, y_prob, threshold=threshold)
    metrics["loss"] = total_loss / total_count if total_count else 0.0
    metrics["samples"] = float(total_count)
    metrics["positive_samples"] = float(sum(1 for value in y_true if value == 1))
    metrics["negative_samples"] = float(sum(1 for value in y_true if value == 0))
    metrics.update({key: float(value) for key, value in confusion_counts(y_true, y_prob, threshold).items()})
    return metrics, predictions


def summarize_groups(predictions: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for prediction in predictions:
        key = (str(prediction.get("label_name", "")), str(prediction.get("method", "")))
        groups[key].append(prediction)

    rows: list[dict[str, object]] = []
    for (label_name, method), items in sorted(groups.items()):
        probs = [float(item["fake_probability"]) for item in items]
        correct = [int(item["correct"]) for item in items]
        predicted_fake = [int(item["predicted_label"]) for item in items]
        rows.append(
            {
                "label_name": label_name,
                "method": method,
                "samples": len(items),
                "mean_fake_probability": float(np.mean(probs)) if probs else 0.0,
                "predicted_fake_rate": float(np.mean(predicted_fake)) if predicted_fake else 0.0,
                "correct_rate": float(np.mean(correct)) if correct else 0.0,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_metric(value: object) -> str:
    if isinstance(value, (int, np.integer)):
        return str(value)
    if isinstance(value, (float, np.floating)):
        value = float(value)
        if math.isnan(value):
            return "nan"
        return f"{value:.4f}"
    return str(value)


def write_summary_markdown(
    path: Path,
    domain_name: str,
    split: str,
    threshold: float,
    metric_rows: list[dict[str, object]],
    group_rows: list[dict[str, object]],
) -> None:
    metric_headers = [
        "model",
        "samples",
        "accuracy",
        "auc",
        "precision",
        "recall",
        "f1",
        "loss",
        "fp",
        "fn",
    ]
    group_headers = [
        "model",
        "label_name",
        "method",
        "samples",
        "mean_fake_probability",
        "predicted_fake_rate",
        "correct_rate",
    ]
    lines = [
        f"# Cross-domain evaluation: {domain_name}",
        "",
        f"- split: `{split}`",
        f"- threshold: `{threshold:.2f}`",
        "",
        "## Overall Metrics",
        "",
        "| " + " | ".join(metric_headers) + " |",
        "| " + " | ".join(["---"] + ["---:"] * (len(metric_headers) - 1)) + " |",
    ]
    for row in metric_rows:
        lines.append("| " + " | ".join(format_metric(row.get(header, "")) for header in metric_headers) + " |")

    lines.extend(
        [
            "",
            "## Group Summary",
            "",
            "| " + " | ".join(group_headers) + " |",
            "| " + " | ".join(["---", "---", "---"] + ["---:"] * (len(group_headers) - 3)) + " |",
        ]
    )
    for row in group_rows:
        lines.append("| " + " | ".join(format_metric(row.get(header, "")) for header in group_headers) + " |")
    lines.extend(
        [
            "",
            "说明：跨域实验不重新训练模型，只替换测试数据。`predicted_fake_rate` 对 real 组可理解为误报率，对 fake 组可理解为召回率。",
        ]
    )
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
    all_rows = read_manifest(manifest_path)
    rows, skipped = filter_rows(
        rows=all_rows,
        data_root=args.data_root,
        split=args.split,
        exclude_fallback=args.exclude_fallback,
    )
    if args.limit is not None:
        rows = rows[: args.limit]
    if not rows:
        raise SystemExit("No evaluable rows found after filtering.")

    domain_name = args.domain_name or infer_domain_name(rows, args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metric_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    group_rows: list[dict[str, object]] = []
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

        print(
            f"evaluating domain={domain_name} model={model_name} split={args.split} samples={len(rows)}",
            flush=True,
        )
        metrics, predictions = evaluate_model(
            model=model,
            model_name=model_name,
            rows=rows,
            data_root=args.data_root,
            image_size=image_size,
            batch_size=args.batch_size,
            threshold=args.threshold,
        )
        metric_row = {
            "domain": domain_name,
            "split": args.split,
            "model": model_name,
            "model_dir": str(model_dir),
            "threshold": args.threshold,
            "samples": int(metrics["samples"]),
            "positive_samples": int(metrics["positive_samples"]),
            "negative_samples": int(metrics["negative_samples"]),
            "accuracy": metrics["accuracy"],
            "auc": metrics["auc"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "loss": metrics["loss"],
            "tp": int(metrics["tp"]),
            "fp": int(metrics["fp"]),
            "tn": int(metrics["tn"]),
            "fn": int(metrics["fn"]),
        }
        metric_rows.append(metric_row)
        for prediction in predictions:
            prediction_rows.append(
                {
                    "domain": domain_name,
                    "model": model_name,
                    **prediction,
                }
            )
        for group_row in summarize_groups(predictions):
            group_rows.append({"domain": domain_name, "model": model_name, **group_row})

    elapsed = time.time() - started_at
    result = {
        "domain": domain_name,
        "manifest": str(manifest_path),
        "data_root": str(args.data_root),
        "split": args.split,
        "threshold": args.threshold,
        "model_dirs": [str(path) for path in model_dirs],
        "input_rows": len(all_rows),
        "evaluated_rows": len(rows),
        "skipped_rows": skipped,
        "elapsed_seconds": round(elapsed, 2),
        "metrics": metric_rows,
        "groups": group_rows,
    }

    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_csv(
        args.output_dir / "metrics.csv",
        metric_rows,
        [
            "domain",
            "split",
            "model",
            "model_dir",
            "threshold",
            "samples",
            "positive_samples",
            "negative_samples",
            "accuracy",
            "auc",
            "precision",
            "recall",
            "f1",
            "loss",
            "tp",
            "fp",
            "tn",
            "fn",
        ],
    )
    write_csv(
        args.output_dir / "group_summary.csv",
        group_rows,
        [
            "domain",
            "model",
            "label_name",
            "method",
            "samples",
            "mean_fake_probability",
            "predicted_fake_rate",
            "correct_rate",
        ],
    )
    write_csv(
        args.output_dir / "predictions.csv",
        prediction_rows,
        [
            "domain",
            "model",
            "split",
            "label",
            "label_name",
            "method",
            "video_stem",
            "face_image_path",
            "source_frame_path",
            "source_video",
            "fallback",
            "fake_probability",
            "predicted_label",
            "predicted_name",
            "correct",
        ],
    )
    write_summary_markdown(
        args.output_dir / "summary.md",
        domain_name=domain_name,
        split=args.split,
        threshold=args.threshold,
        metric_rows=metric_rows,
        group_rows=group_rows,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
