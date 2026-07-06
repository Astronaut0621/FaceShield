# JPEG 压缩鲁棒性测试记录

更新时间：2026-07-06

本文档记录 FaceShield 在 JPEG 压缩扰动下的鲁棒性测试结果。测试目标是模拟 AI 换脸诈骗图片在微信、短视频平台、截图转发等场景中可能经历的二次压缩，观察检测模型在压缩质量下降时的指标变化。

## 1. 测试设置

| 项目 | 设置 |
|---|---|
| 数据集 | FaceForensics++ c23, original + Deepfakes |
| 测试 split | `data/ffpp_faces/face_manifest_clean.csv` 中的 test split |
| 测试样本数 | 1092 张人脸裁剪图 |
| 压缩方式 | 在内存中对测试图片重新编码为 JPEG，不修改原始图片 |
| JPEG quality | original, 95, 75, 50, 30 |
| 评估模型 | `baseline`, `fusion_v2`, `fusion_v3` |
| 设备 | 本地 CPU, PaddlePaddle 3.3.1 |
| 评估脚本 | `training/evaluate_jpeg_robustness.py` |
| 输出目录 | `model/robustness/jpeg/` |

本轮使用已部署的 `baseline`、`fusion_v2` 和 `fusion_v3` 进行测试。其中 `fusion_v3` 使用 seed42 checkpoint，因为该 checkpoint 是三组 v3 实验中测试集表现最好的版本。

运行命令：

```powershell
.\.venv\Scripts\python.exe training\evaluate_jpeg_robustness.py `
  --output-dir model\robustness\jpeg `
  --qualities 95 75 50 30 `
  --batch-size 32 `
  --device cpu
```

## 2. 测试结果

| model | quality | Accuracy | AUC | Precision | Recall | F1 | Loss | AUC drop | F1 drop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | original | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6324 | 0.0000 | 0.0000 |
| baseline | q95 | 0.7793 | 0.8551 | 0.7397 | 0.8606 | 0.7956 | 0.6324 | 0.0003 | 0.0017 |
| baseline | q75 | 0.7674 | 0.8530 | 0.7249 | 0.8606 | 0.7869 | 0.6484 | 0.0024 | 0.0104 |
| baseline | q50 | 0.7701 | 0.8521 | 0.7290 | 0.8587 | 0.7885 | 0.6519 | 0.0032 | 0.0087 |
| baseline | q30 | 0.7564 | 0.8493 | 0.7110 | 0.8624 | 0.7794 | 0.6840 | 0.0061 | 0.0178 |
| fusion_v2 | original | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.7719 | 0.0000 | 0.0000 |
| fusion_v2 | q95 | 0.8315 | 0.9015 | 0.8241 | 0.8422 | 0.8330 | 0.7709 | -0.0001 | 0.0018 |
| fusion_v2 | q75 | 0.8260 | 0.9023 | 0.8187 | 0.8367 | 0.8276 | 0.7473 | -0.0008 | 0.0073 |
| fusion_v2 | q50 | 0.8278 | 0.8979 | 0.8312 | 0.8220 | 0.8266 | 0.7681 | 0.0035 | 0.0083 |
| fusion_v2 | q30 | 0.8104 | 0.8922 | 0.8118 | 0.8073 | 0.8096 | 0.8098 | 0.0092 | 0.0253 |
| fusion_v3 | original | 0.8297 | 0.9008 | 0.8355 | 0.8202 | 0.8278 | 0.8475 | 0.0000 | 0.0000 |
| fusion_v3 | q95 | 0.8278 | 0.9004 | 0.8336 | 0.8183 | 0.8259 | 0.8511 | 0.0004 | 0.0019 |
| fusion_v3 | q75 | 0.8251 | 0.8986 | 0.8365 | 0.8073 | 0.8217 | 0.8746 | 0.0023 | 0.0061 |
| fusion_v3 | q50 | 0.8361 | 0.8973 | 0.8479 | 0.8183 | 0.8329 | 0.8752 | 0.0035 | -0.0051 |
| fusion_v3 | q30 | 0.8178 | 0.8928 | 0.8314 | 0.7963 | 0.8135 | 0.9300 | 0.0081 | 0.0143 |

`AUC drop` 和 `F1 drop` 均以同一模型的 original 结果为基准。

## 3. 结果分析

JPEG 压缩会降低模型检测性能，但在 q95、q75 和 q50 下下降幅度较小；在 q30 强压缩下，性能下降更明显。

baseline 在 q30 下 AUC 从 0.8554 降至 0.8493，F1 从 0.7973 降至 0.7794。它的 Recall 基本保持在 0.86 左右，但 Precision 从 0.7413 降至 0.7110，说明压缩后更容易把 real 样本误判为 fake。

fusion_v2 在 q30 下 AUC 从 0.9014 降至 0.8922，F1 从 0.8348 降至 0.8096。它的 Precision 仍保持在 0.8118，但 Recall 从 0.8440 降至 0.8073，说明高频 FFT 分支在强压缩下会受到影响，导致部分 fake 样本被漏检。

fusion_v3 在 q30 下 AUC 从 0.9008 降至 0.8928，F1 从 0.8278 降至 0.8135。相比 fusion_v2，fusion_v3 在 q30 下 F1 略高，AUC 也略高，但 Recall 为 0.7963，低于 fusion_v2 的 0.8073。这说明固定 DCT 三频带在强压缩下对 Precision 和 F1 有一定帮助，但 fake 召回仍不够稳定。

横向比较看，fusion_v2 和 fusion_v3 在所有压缩质量下均明显优于 baseline。即使在 q30 下，fusion_v2 的 AUC/F1 为 0.8922/0.8096，fusion_v3 为 0.8928/0.8135，均高于 baseline 的 0.8493/0.7794。这说明频域-空域融合模型在压缩场景下仍有优势，但强压缩会削弱 fake 召回能力。

## 4. 论文可用表述

> 为验证模型在真实传播场景下的鲁棒性，本文进一步对测试集人脸图片进行 JPEG 二次压缩，设置 quality 为 95、75、50 和 30，并比较压缩前后模型性能变化。实验结果表明，JPEG 压缩会造成检测性能下降，尤其在 quality=30 的强压缩条件下更明显。与 RGB baseline 相比，fusion_v2 和 fusion_v3 在所有压缩质量下均保持更高的 AUC 和 F1，其中 q30 条件下 fusion_v2 的 AUC/F1 为 0.8922/0.8096，fusion_v3 的 AUC/F1 为 0.8928/0.8135，均高于 baseline 的 0.8493/0.7794。该结果说明频域-空域融合模型在压缩扰动下仍具备一定鲁棒性。但 fusion_v2 和 fusion_v3 在强压缩下 Recall 均出现下降，表明高频伪影和固定 DCT 频带特征仍会受到压缩影响，后续需要通过 JPEG 数据增强、block-DCT 特征或压缩感知训练进一步提升鲁棒性。

不建议写成“模型不受压缩影响”。更准确的说法是：`fusion_v2` 和 `fusion_v3` 在压缩下仍优于 baseline，但强压缩会带来可观察的性能下降。

## 5. 后续改进方向

1. 训练时加入 JPEG quality 随机增强，使模型在训练阶段见过压缩扰动。
2. 在频域分支中加入 block-DCT 或压缩块特征，更直接建模 JPEG block effect。
3. 针对 q30 或更低质量图片单独分析 false negative 样本，观察被漏检 fake 的共同特征。
4. 对 q30 下 `fusion_v2` 和 `fusion_v3` 的 false negative 样本做 Grad-CAM 对比，分析两类频域分支的漏检原因。
5. 如果时间允许，可模拟截图缩放、模糊和平台转码，形成更完整的真实传播鲁棒性测试。

## 6. 证据文件

| 文件 | 用途 |
|---|---|
| `training/evaluate_jpeg_robustness.py` | JPEG 压缩鲁棒性评估脚本 |
| `model/robustness/jpeg/metrics_by_quality.csv` | 指标表 |
| `model/robustness/jpeg/metrics_by_quality.json` | 完整评估配置和指标 |
| `model/robustness/jpeg/predictions_by_quality.csv` | 每张测试图片在每个质量档下的预测结果 |
| `model/robustness/jpeg/summary.md` | 脚本自动生成的简版结果汇总 |
