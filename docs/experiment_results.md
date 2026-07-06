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
| learning rate | baseline/fusion_fft 为 0.001；fusion_v2 主配置为 0.0005 |
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

### 3.3 fusion_v2 调参记录

| 配置 | seed | freeze-spatial-epochs | lr | best epoch | val AUC | test Accuracy | test AUC | Recall | F1 | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 主配置 | 42 | 3 | 5e-4 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8440 | 0.8348 | 当前最好 |
| 配置 A | 42 | 0 | 3e-4 | 1 | 0.8595 | 0.8022 | 0.8718 | 0.7633 | 0.7939 | 不采用 |
| 配置 B | 42 | 1 | 3e-4 | 22 | 0.8681 | 0.7912 | 0.8940 | 0.7064 | 0.7715 | Recall 太低，不采用 |
| 配置 C | 42 | 3 | 3e-4 | 14 | 0.8616 | 0.7958 | 0.8887 | 0.7450 | 0.7845 | 降低学习率后退步，不采用 |

## 4. 结果分析

初版实验中，RGB baseline 的整体表现明显优于 fusion_fft。baseline 的 test AUC 为 0.8554，test F1 为 0.7973；fusion_fft 的 test AUC 为 0.7617，test F1 为 0.6980。

这说明当前轻量级 CNN 和小规模 FaceForensics++ 子集条件下，直接将 FFT 幅度谱作为第二分支并与 RGB 特征 concat，没有带来性能提升。可能原因包括：

1. FFT 幅度谱保留的是全局频域信息，局部伪造痕迹表达不足。
2. 当前频域分支较浅，学习到的高频伪影特征不够稳定。
3. 简单 concat 融合无法判断 RGB 特征与频域特征在不同样本中的可靠性。
4. 训练集规模偏小，增加频域分支后模型参数量增大，更容易过拟合。

基于该问题，后续实现了 fusion_v2：将频域输入从完整 FFT 幅度谱改为高频 FFT，使用 baseline checkpoint 初始化 spatial branch，并采用 gating residual fusion 替代简单 concat。三组 seed 平均结果显示，fusion_v2 的 AUC、Accuracy 和 F1 均略高于 baseline，说明频域信息经过更合理的特征构建和融合策略后能够形成一定补充。

但是，fusion_v2 的提升幅度不大，且按相同 seed 对比时并非每次都优于 baseline。因此论文或答辩中应表述为“带来一定提升”，不能表述为“显著提升”。当前推荐采用 `fusion_v2 + spatial checkpoint + freeze 3 epochs + lr=5e-4` 作为频域-空域融合主模型，同时保留 baseline 作为对照模型。

## 5. 后续改进方向

1. 在当前高频 FFT 基础上继续尝试环形频带统计、多尺度 FFT。
2. 增加 DCT 或 block-DCT 特征，更贴近 JPEG 压缩和局部伪影。
3. 在当前 gating fusion 基础上继续尝试 attention 或 cross-modal interaction，让模型动态调整 RGB 与频域特征权重。
4. 将 backbone 从轻量 CNN 升级为 ResNet18、MobileNetV3 或 EfficientNet，并加入更强正则化。
5. 扩展 fake 类型到 Face2Face、FaceSwap 和 NeuralTextures，验证跨伪造方法泛化能力。
