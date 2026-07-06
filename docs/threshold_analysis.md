# fusion_v2 阈值敏感性测试记录

更新时间：2026-07-06

本文档记录 FaceShield 主模型 `fusion_v2` 在不同 fake probability 阈值下的 Precision、Recall、F1 和混淆矩阵变化。测试目的不是重新训练模型，而是在已得到的预测概率基础上，分析二分类阈值对 fake 漏检和 real 误报的影响，并据此确定业务展示层的风险等级边界。

## 1. 测试设置

| 项目 | 设置 |
|---|---|
| 模型 | `fusion_v2` |
| 数据 | FaceForensics++ clean test split |
| 样本数 | 1092 |
| fake 样本数 | 545 |
| real 样本数 | 547 |
| 概率来源 | `model/robustness/jpeg/predictions_by_quality.csv` 中 `fusion_v2 + original` |
| 输出目录 | `model/thresholds/fusion_v2_original/` |

运行命令：

```powershell
.\.venv\Scripts\python.exe training\evaluate_thresholds.py `
  --predictions model\robustness\jpeg\predictions_by_quality.csv `
  --model fusion_v2 `
  --quality original `
  --output-dir model\thresholds\fusion_v2_original
```

## 2. 阈值测试结果

| threshold | Accuracy | Precision | Recall | F1 | FP | FN | FPR | FNR |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 0.8196 | 0.7871 | 0.8752 | 0.8288 | 129 | 68 | 0.2358 | 0.1248 |
| 0.25 | 0.8233 | 0.7953 | 0.8697 | 0.8309 | 122 | 71 | 0.2230 | 0.1303 |
| 0.30 | 0.8269 | 0.8038 | 0.8642 | 0.8329 | 115 | 74 | 0.2102 | 0.1358 |
| 0.35 | 0.8297 | 0.8079 | 0.8642 | 0.8351 | 112 | 74 | 0.2048 | 0.1358 |
| 0.40 | 0.8297 | 0.8111 | 0.8587 | 0.8342 | 109 | 77 | 0.1993 | 0.1413 |
| 0.45 | 0.8306 | 0.8191 | 0.8477 | 0.8332 | 102 | 83 | 0.1865 | 0.1523 |
| 0.50 | 0.8333 | 0.8259 | 0.8440 | 0.8348 | 97 | 85 | 0.1773 | 0.1560 |
| 0.55 | 0.8315 | 0.8252 | 0.8404 | 0.8327 | 97 | 87 | 0.1773 | 0.1596 |
| 0.60 | 0.8288 | 0.8255 | 0.8330 | 0.8292 | 96 | 91 | 0.1755 | 0.1670 |
| 0.65 | 0.8342 | 0.8370 | 0.8294 | 0.8332 | 88 | 93 | 0.1609 | 0.1706 |
| 0.70 | 0.8315 | 0.8361 | 0.8239 | 0.8299 | 88 | 96 | 0.1609 | 0.1761 |
| 0.75 | 0.8342 | 0.8434 | 0.8202 | 0.8316 | 83 | 98 | 0.1517 | 0.1798 |
| 0.80 | 0.8342 | 0.8500 | 0.8110 | 0.8300 | 78 | 103 | 0.1426 | 0.1890 |

## 3. 结果分析

默认阈值 0.50 下，`fusion_v2` 的 Precision 为 0.8259，Recall 为 0.8440，F1 为 0.8348，fake 漏检数 FN 为 85。

当二分类阈值降低到 0.35 时，Recall 提升到 0.8642，F1 提升到 0.8351，是本轮扫描中的最高 F1；fake 漏检数从 85 降至 74，减少 11 张漏检 fake。但代价是 real 误报数 FP 从 97 增加到 112，多 15 张 real 会被二分类阈值判为 fake。因此系统不把 0.35 直接作为最终 fake 结论阈值，而是将其作为 low 和 medium 的风险分界。

当阈值提高到 0.80 时，Precision 提升到 0.8500，但 Recall 降至 0.8110，fake 漏检数增加到 103。对于 AI 换脸诈骗检测场景，这种策略会降低误报，但 fake 漏检风险更高，不适合作为默认反诈策略。

## 4. 推荐展示策略

| 使用场景 | 阈值/边界 | 理由 |
|---|---:|---|
| 论文主实验对比 | 0.50 | 与常规二分类默认阈值一致，方便和训练结果对比 |
| low/medium 风险分界 | 0.35 | 保留更敏感的风险提示，但不直接下 fake 结论 |
| high 风险分界 | 0.80 | 提高高风险提示的 Precision，减少 real 被强提示为高风险 |

综合反诈骗场景，系统保留模型原始 fake probability 和默认二分类 `label`，前端主展示使用分级风险：

```text
fake_probability < 0.35        -> low
0.35 <= fake_probability < 0.80 -> medium
fake_probability >= 0.80       -> high
```

这样既不改变模型二分类输出，也能避免把中等概率样本直接展示成确定伪造。`medium` 表示建议人工复核，不等同于伪造结论。

## 5. 论文可用表述

> 为进一步分析模型输出阈值对检测性能的影响，本文基于 `fusion_v2` 在测试集上的 fake probability 输出进行阈值敏感性测试。结果表明，默认二分类阈值 0.50 下模型 F1 为 0.8348，Recall 为 0.8440；当阈值降低到 0.35 时，Recall 提升到 0.8642，F1 达到 0.8351，同时 fake 漏检数从 85 降至 74，但 real 误报数从 97 增加到 112。综合考虑误报展示和反诈骗场景中的漏检风险，系统最终保留 real/fake 二分类 label 和连续 fake probability，并在业务层将概率映射为 low、medium、high 三档风险等级。其中 medium 表示建议人工复核，不等同于伪造结论。

## 6. 证据文件

| 文件 | 用途 |
|---|---|
| `training/evaluate_thresholds.py` | 阈值敏感性评估脚本 |
| `model/thresholds/fusion_v2_original/metrics_by_threshold.csv` | 阈值指标表 |
| `model/thresholds/fusion_v2_original/metrics_by_threshold.json` | 完整结果和推荐项 |
| `model/thresholds/fusion_v2_original/summary.md` | 自动生成的简版结果 |
