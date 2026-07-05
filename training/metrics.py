from __future__ import annotations

import numpy as np


def binary_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = np.asarray(y_true).astype("int64")
    y_score = np.asarray(y_score).astype("float64")
    pos = int((y_true == 1).sum())
    neg = int((y_true == 0).sum())
    if pos == 0 or neg == 0:
        return float("nan")

    order = np.argsort(y_score)
    sorted_scores = y_score[order]
    ranks = np.empty_like(sorted_scores, dtype="float64")
    i = 0
    while i < len(sorted_scores):
        j = i + 1
        while j < len(sorted_scores) and sorted_scores[j] == sorted_scores[i]:
            j += 1
        average_rank = (i + 1 + j) / 2.0
        ranks[i:j] = average_rank
        i = j

    original_ranks = np.empty_like(ranks)
    original_ranks[order] = ranks
    sum_pos_ranks = original_ranks[y_true == 1].sum()
    return float((sum_pos_ranks - pos * (pos + 1) / 2.0) / (pos * neg))


def classification_metrics(y_true: list[int], y_prob: list[float], threshold: float = 0.5) -> dict[str, float]:
    y_true_arr = np.asarray(y_true, dtype="int64")
    y_prob_arr = np.asarray(y_prob, dtype="float64")
    y_pred = (y_prob_arr >= threshold).astype("int64")

    accuracy = float((y_pred == y_true_arr).mean()) if len(y_true_arr) else 0.0
    tp = int(((y_pred == 1) & (y_true_arr == 1)).sum())
    fp = int(((y_pred == 1) & (y_true_arr == 0)).sum())
    fn = int(((y_pred == 0) & (y_true_arr == 1)).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    auc = binary_auc(y_true_arr, y_prob_arr)
    return {
        "accuracy": accuracy,
        "auc": auc,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }
