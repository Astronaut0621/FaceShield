# FaceShield 实验结果整理

## 1. 文件整理

本次从 AutoDL 传回的训练结果保存在：

```text
model/outputs/
├─ baseline/
│  ├─ best.pdparams
│  ├─ config.json
│  ├─ history.json
│  ├─ best_metrics.json
│  └─ test_metrics.json
├─ fusion_fft/
│  ├─ best.pdparams
│  ├─ config.json
│  ├─ history.json
│  ├─ best_metrics.json
│  └─ test_metrics.json
└─ fusion_v2_seed*/
   ├─ best.pdparams
   ├─ config.json
   ├─ history.json
   ├─ best_metrics.json
   └─ test_metrics.json
└─ fusion_v3_seed*/
   ├─ best.pdparams
   ├─ config.json
   ├─ history.json
   ├─ best_metrics.json
   └─ test_metrics.json
```

已整理出的汇总文件保存在：

```text
model/summary/
├─ metrics_summary.csv
├─ epoch_history.csv
├─ training_curves.svg
└─ experiment_summary.md
```

其中，`metrics_summary.csv` 用于论文或答辩中的最终指标表，`epoch_history.csv` 用于后续画训练曲线，`training_curves.svg` 为验证集 AUC 和 Accuracy 曲线，`experiment_summary.md` 为简版实验总结。

## 2. 实验设置

| 项目 | 设置 |
|---|---|
| 数据集 | FaceForensics++ c23, original + Deepfakes |
| 输入数据 | 224x224 人脸裁剪图 |
| 数据划分 | train 3769, val 1284, test 1092 |
| 训练框架 | PaddlePaddle 2.4.0 |
| 训练设备 | RTX 3080 Ti, `gpu:0` |
| batch size | 32 |
| learning rate | baseline/fusion_fft 为 0.001；fusion_v2/fusion_v3 主配置为 0.0005 |
| weight decay | 0.0001 |
| dropout | 0.3 |
| early stopping patience | 8 |

## 3. 模型对比

### 3.1 初版模型对比

| 模型 | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 14 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 |
| fusion_fft | 15 | 0.7678 | 0.6941 | 0.7617 | 0.6881 | 0.7083 | 0.6980 | 0.9340 |

### 3.2 fusion_v2 三 seed 结果

主配置为：

```text
model=fusion_v2
lr=5e-4
spatial_checkpoint=outputs/baseline/best.pdparams
freeze_spatial_epochs=3
```

| 模型 | seed | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 42 | 14 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 |
| baseline | 7 | 28 | 0.8552 | 0.7866 | 0.8786 | 0.7727 | 0.8110 | 0.7914 | 0.7825 |
| baseline | 123 | 16 | 0.8589 | 0.8223 | 0.9074 | 0.8343 | 0.8037 | 0.8187 | 0.4803 |
| fusion_v2 | 42 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.7719 |
| fusion_v2 | 7 | 2 | 0.8446 | 0.7821 | 0.8632 | 0.7902 | 0.7670 | 0.7784 | 0.8182 |
| fusion_v2 | 123 | 5 | 0.8627 | 0.8013 | 0.8948 | 0.7706 | 0.8569 | 0.8115 | 0.7485 |

| 模型 | Accuracy | AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|
| baseline 平均 | 0.7967 | 0.8805 | 0.7828 | 0.8257 | 0.8025 | 0.6318 |
| fusion_v2 平均 | 0.8056 | 0.8865 | 0.7956 | 0.8226 | 0.8082 | 0.7795 |
| fusion_v2 - baseline | +0.0089 | +0.0060 | +0.0128 | -0.0031 | +0.0058 | +0.1477 |

### 3.3 fusion_v3 DCT 三频带实验

fusion_v3 是参考 DCT 频域三频带思想后的轻量化实现，结构为：

```text
RGB spatial branch
+ fixed DCT low/mid/high frequency bands
+ gated residual fusion
-> real/fake classifier
```

需要注意，当前 fusion_v3 使用的是固定低/中/高三频带，不是论文中的动态三频带划分，也没有引入 EfficientNet_B4、Transformer 或 Q-K-V 融合。因此它更适合作为 DCT 方向的消融实验和后续改进依据。

| 模型 | seed | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fusion_v3 | 42 | 14 | 0.8660 | 0.8297 | 0.9008 | 0.8355 | 0.8202 | 0.8278 | 0.8475 |
| fusion_v3 | 7 | 1 | 0.8458 | 0.7839 | 0.8656 | 0.8084 | 0.7431 | 0.7744 | 0.6811 |
| fusion_v3 | 123 | 5 | 0.8636 | 0.7995 | 0.8983 | 0.7810 | 0.8312 | 0.8053 | 0.7181 |

| 模型 | Accuracy | AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|
| baseline 平均 | 0.7967 | 0.8805 | 0.7828 | 0.8257 | 0.8025 | 0.6318 |
| fusion_v2 平均 | 0.8056 | 0.8865 | 0.7956 | 0.8226 | 0.8082 | 0.7795 |
| fusion_v3 平均 | 0.8043 | 0.8882 | 0.8083 | 0.7982 | 0.8025 | 0.7489 |
| fusion_v3 - baseline | +0.0076 | +0.0077 | +0.0255 | -0.0275 | +0.0000 | +0.1171 |
| fusion_v3 - fusion_v2 | -0.0013 | +0.0017 | +0.0127 | -0.0244 | -0.0057 | -0.0306 |

结果解读：

1. fusion_v3 的三 seed 平均 AUC 为 0.8882，略高于 fusion_v2 的 0.8865 和 baseline 的 0.8805，说明 DCT 频带特征具备继续优化价值。
2. fusion_v3 的平均 Precision 最高，但平均 Recall 低于 fusion_v2 和 baseline，说明它对 fake 样本更保守，存在漏检风险。
3. 面向 AI 换脸诈骗检测，Recall 和 F1 对实际风险更敏感，因此当前不建议用 fusion_v3 替代 fusion_v2 作为主模型。
4. 论文中可以将 fusion_v3 写成“参考 DCT 三频带思想的进一步探索”，并把动态 DCT 频带、attention/Q-K-V 融合作为后续改进方向。

### 3.4 fusion_v2 调参记录

| 配置 | seed | freeze-spatial-epochs | lr | best epoch | val AUC | test Accuracy | test AUC | Recall | F1 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 主配置 | 42 | 3 | 5e-4 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8440 | 0.8348 | 当前最好 |
| 配置 A | 42 | 0 | 3e-4 | 1 | 0.8595 | 0.8022 | 0.8718 | 0.7633 | 0.7939 | 不采用 |
| 配置 B | 42 | 1 | 3e-4 | 22 | 0.8681 | 0.7912 | 0.8940 | 0.7064 | 0.7715 | Recall 太低，不采用 |
| 配置 C | 42 | 3 | 3e-4 | 14 | 0.8616 | 0.7958 | 0.8887 | 0.7450 | 0.7845 | 降低学习率后退步，不采用 |

### 3.5 JPEG 压缩鲁棒性测试

为模拟 AI 换脸诈骗图片在社交平台、截图转发和即时通信软件中可能经历的二次压缩，本轮对 test split 的 1092 张人脸裁剪图进行了 JPEG 重新编码测试。压缩在内存中完成，不修改原始测试图片。测试质量档为 original、q95、q75、q50 和 q30。

本轮评估已部署的 `baseline`、`fusion_v2` 和 `fusion_v3`。其中 `fusion_v3` 使用 seed42 checkpoint。完整记录见 `docs/jpeg_robustness_results.md`，输出文件位于 `model/robustness/jpeg/`。

| 模型 | quality | Accuracy | AUC | Precision | Recall | F1 | AUC drop | F1 drop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | original | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.0000 | 0.0000 |
| baseline | q75 | 0.7674 | 0.8530 | 0.7249 | 0.8606 | 0.7869 | 0.0024 | 0.0104 |
| baseline | q30 | 0.7564 | 0.8493 | 0.7110 | 0.8624 | 0.7794 | 0.0061 | 0.0178 |
| fusion_v2 | original | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.0000 | 0.0000 |
| fusion_v2 | q75 | 0.8260 | 0.9023 | 0.8187 | 0.8367 | 0.8276 | -0.0008 | 0.0073 |
| fusion_v2 | q30 | 0.8104 | 0.8922 | 0.8118 | 0.8073 | 0.8096 | 0.0092 | 0.0253 |
| fusion_v3 | original | 0.8297 | 0.9008 | 0.8355 | 0.8202 | 0.8278 | 0.0000 | 0.0000 |
| fusion_v3 | q75 | 0.8251 | 0.8986 | 0.8365 | 0.8073 | 0.8217 | 0.0023 | 0.0061 |
| fusion_v3 | q30 | 0.8178 | 0.8928 | 0.8314 | 0.7963 | 0.8135 | 0.0081 | 0.0143 |

结果显示，JPEG 压缩会造成模型性能下降，q30 强压缩下下降更明显。fusion_v2 和 fusion_v3 在所有压缩质量下均保持高于 baseline 的 AUC 和 F1，说明频域-空域融合模型在压缩场景下仍有优势。q30 下，fusion_v3 的 AUC/F1 为 0.8928/0.8135，略高于 fusion_v2 的 0.8922/0.8096；但 fusion_v3 的 Recall 为 0.7963，低于 fusion_v2 的 0.8073，说明固定 DCT 三频带在强压缩下对 F1 有帮助，但 fake 召回仍不够稳定。

### 3.6 fusion_v2 阈值敏感性测试

本轮基于 `fusion_v2` 在 original test split 上的 fake probability 输出，扫描 0.20 到 0.80 的二分类判定阈值。完整结果见 `docs/threshold_analysis.md`。

| threshold | Accuracy | Precision | Recall | F1 | FP | FN | 判断 |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0.35 | 0.8297 | 0.8079 | 0.8642 | 0.8351 | 112 | 74 | F1 最高，可作 low/medium 风险分界 |
| 0.40 | 0.8297 | 0.8111 | 0.8587 | 0.8342 | 109 | 77 | Recall 较高但误报增加 |
| 0.50 | 0.8333 | 0.8259 | 0.8440 | 0.8348 | 97 | 85 | 默认二分类阈值 |
| 0.65 | 0.8342 | 0.8370 | 0.8294 | 0.8332 | 88 | 93 | 更保守，误报更少 |
| 0.80 | 0.8342 | 0.8500 | 0.8110 | 0.8300 | 78 | 103 | Precision 最高但漏检增加 |

结果显示，默认二分类阈值 0.50 已经较稳定；threshold=0.35 时，Recall 从 0.8440 提升到 0.8642，FN 从 85 降到 74，但 FP 从 97 增加到 112。考虑到 real 误报展示影响，系统不把 0.35 直接作为 fake 结论阈值，而是保留 `fake_probability`，并将 0.35/0.80 作为 low、medium、high 风险等级边界。

## 4. 结果分析

初版实验中，RGB baseline 的整体表现明显优于 fusion_fft。baseline 的 test AUC 为 0.8554，test F1 为 0.7973；fusion_fft 的 test AUC 为 0.7617，test F1 为 0.6980。

这说明当前轻量级 CNN 和小规模 FaceForensics++ 子集条件下，直接将 FFT 幅度谱作为第二分支并与 RGB 特征 concat，没有带来性能提升。可能原因包括：

1. FFT 幅度谱保留的是全局频域信息，局部伪造痕迹表达不足。
2. 当前频域分支较浅，学习到的高频伪影特征不够稳定。
3. 简单 concat 融合无法判断 RGB 特征与频域特征在不同样本中的可靠性。
4. 训练集规模偏小，增加频域分支后模型参数量增大，更容易过拟合。

基于该问题，后续实现了 fusion_v2：将频域输入从完整 FFT 幅度谱改为高频 FFT，使用 baseline checkpoint 初始化 spatial branch，并采用 gating residual fusion 替代简单 concat。三组 seed 平均结果显示，fusion_v2 的 AUC、Accuracy 和 F1 均略高于 baseline，说明频域信息经过更合理的特征构建和融合策略后能够形成一定补充。

进一步参考文献中的 DCT 频带建模思想后，实现了 fusion_v3。fusion_v3 的三 seed 平均 AUC 略高于 fusion_v2，但 Recall 和 F1 低于 fusion_v2，说明固定 DCT 三频带对判别边界有帮助，但对 fake 样本召回不够稳定。

JPEG 压缩鲁棒性测试进一步表明，压缩会降低模型性能，尤其在 q30 强压缩下更明显。fusion_v2 在 q30 下取得 0.8922 的 AUC 和 0.8096 的 F1，fusion_v3 取得 0.8928 的 AUC 和 0.8135 的 F1，均高于 baseline 的 0.8493 和 0.7794，说明频域-空域融合模型在压缩场景中仍保留优势。但 fusion_v2 的 Recall 从 0.8440 降至 0.8073，fusion_v3 的 Recall 从 0.8202 降至 0.7963，提示高频伪影和固定 DCT 频带线索都会受到强压缩影响。

阈值敏感性测试说明，模型输出的 fake probability 可以在业务层根据风险偏好进行解释。默认 threshold=0.50 适合论文主实验对比；threshold=0.35 能将 fake 漏检数从 85 降到 74，但会增加 real 误报。因此系统展示层采用“伪造概率 + 风险等级”为主，`label` 只保留为模型二分类结果。

因此，论文或答辩中应表述为“带来一定提升”，不能表述为“显著提升”。当前推荐采用 `fusion_v2 + spatial checkpoint + freeze 3 epochs + lr=5e-4` 作为频域-空域融合主模型，同时将 fusion_v3 作为 DCT 频带建模消融实验和后续改进依据。

## 5. 后续改进方向

1. 在当前高频 FFT 基础上继续尝试环形频带统计、多尺度 FFT。
2. 将 fusion_v3 的固定 DCT 三频带升级为动态频带选择或 block-DCT，使频域特征更贴近 JPEG 压缩和局部伪影。
3. 在当前 gating fusion 基础上继续尝试 attention、Q-K-V 或 cross-modal interaction，让模型动态调整 RGB 与频域特征权重。
4. 基于已完成的 JPEG 压缩鲁棒性测试，在训练阶段加入 JPEG 随机增强，并继续补充缩放、模糊和截图转发等扰动。
5. 将 backbone 从轻量 CNN 升级为 ResNet18、MobileNetV3 或 EfficientNet，并加入更强正则化。
6. 扩展 fake 类型到 Face2Face、FaceSwap 和 NeuralTextures，验证跨伪造方法泛化能力。
