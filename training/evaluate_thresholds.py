from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from metrics import classification_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate decision thresholds from saved predictions.")
    parser.add_argument(
        "--predictions",
        type=Path,
        default=Path("model/robustness/jpeg/predictions_by_quality.csv"),
    )
    parser.add_argument("--model", default="fusion_v2")
    parser.add_argument("--quality", default="original")
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80],
    )
    parser.add_argument("--output-dir", type=Path, default=Path("model/thresholds/fusion_v2_original"))
    return parser.parse_args()


def load_rows(path: Path, model_name: str, quality: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = [
            row
            for row in csv.DictReader(f)
            if row["model"] == model_name and row["quality"] == quality
        ]
    if not rows:
        raise ValueError(f"No rows found for model={model_name}, quality={quality}: {path}")
    return rows


def confusion_counts(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict[str, int]:
    y_pred = (y_prob >= threshold).astype("int64")
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "predicted_fake": int((y_pred == 1).sum()),
        "predicted_real": int((y_pred == 0).sum()),
    }


def evaluate_thresholds(rows: list[dict[str, str]], thresholds: list[float]) -> list[dict[str, float | int]]:
    y_true = np.array([int(row["label"]) for row in rows], dtype="int64")
    y_prob = np.array([float(row["fake_probability"]) for row in rows], dtype="float64")
    results: list[dict[str, float | int]] = []
    for threshold in thresholds:
        metrics = classification_metrics(y_true.tolist(), y_prob.tolist(), threshold=threshold)
        counts = confusion_counts(y_true, y_prob, threshold)
        false_positive_rate = counts["fp"] / (counts["fp"] + counts["tn"]) if (counts["fp"] + counts["tn"]) else 0.0
        false_negative_rate = counts["fn"] / (counts["fn"] + counts["tp"]) if (counts["fn"] + counts["tp"]) else 0.0
        results.append(
            {
                "threshold": float(threshold),
                "samples": int(len(rows)),
                **metrics,
                **counts,
                "false_positive_rate": float(false_positive_rate),
                "false_negative_rate": float(false_negative_rate),
            }
        )
    return results


def write_csv(path: Path, rows: list[dict[str, float | int]]) -> None:
    fieldnames = [
        "threshold",
        "samples",
        "accuracy",
        "auc",
        "precision",
        "recall",
        "f1",
        "tp",
        "fp",
        "tn",
        "fn",
        "predicted_fake",
        "predicted_real",
        "false_positive_rate",
        "false_negative_rate",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def best_rows(results: list[dict[str, float | int]]) -> dict[str, dict[str, float | int]]:
    best_f1 = max(results, key=lambda row: float(row["f1"]))
    best_recall_f1 = max(
        (row for row in results if float(row["recall"]) >= 0.85),
        key=lambda row: float(row["f1"]),
        default=best_f1,
    )
    balanced = min(
        results,
        key=lambda row: (
            abs(float(row["recall"]) - float(row["precision"])),
            -float(row["f1"]),
        ),
    )
    return {
        "best_f1": best_f1,
        "best_f1_with_recall_at_least_0.85": best_recall_f1,
        "most_balanced_precision_recall": balanced,
    }


def fmt(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.4f}"


def write_summary(path: Path, model: str, quality: str, results: list[dict[str, float | int]], picks: dict[str, dict[str, float | int]]) -> None:
    headers = ["threshold", "accuracy", "precision", "recall", "f1", "fp", "fn", "false_positive_rate", "false_negative_rate"]
    lines = [
        "# 阈值敏感性测试",
        "",
        f"模型：`{model}`",
        f"输入预测：`{quality}`",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---:"] * len(headers)) + " |",
    ]
    for row in results:
        lines.append("| " + " | ".join(fmt(row[header]) for header in headers) + " |")
    lines.append("")
    lines.append("## 推荐")
    lines.append("")
    for name, row in picks.items():
        lines.append(
            f"- `{name}`: threshold={fmt(row['threshold'])}, precision={fmt(row['precision'])}, "
            f"recall={fmt(row['recall'])}, f1={fmt(row['f1'])}, fp={row['fp']}, fn={row['fn']}"
        )
    lines.append("")
    lines.append("说明：较低二分类阈值可以提高 Recall，但也会增加 real 误报；系统展示层应保留 fake probability，并将阈值结果作为风险等级边界依据。")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    rows = load_rows(args.predictions, args.model, args.quality)
    results = evaluate_thresholds(rows, args.thresholds)
    picks = best_rows(results)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "metrics_by_threshold.csv", results)
    output = {
        "predictions": str(args.predictions),
        "model": args.model,
        "quality": args.quality,
        "thresholds": args.thresholds,
        "metrics": results,
        "recommendations": picks,
    }
    (args.output_dir / "metrics_by_threshold.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_summary(args.output_dir / "summary.md", args.model, args.quality, results, picks)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
