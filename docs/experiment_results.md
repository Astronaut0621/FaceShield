# FaceShield 实验结果整理

## 1. 文件整理

本次从 AutoDL 传回的训练结果保存在：

```text
faceshield_outputs/outputs/
├─ baseline/
│  ├─ best.pdparams
│  ├─ config.json
│  ├─ history.json
│  ├─ best_metrics.json
│  └─ test_metrics.json
└─ fusion_fft/
   ├─ best.pdparams
   ├─ config.json
   ├─ history.json
   ├─ best_metrics.json
   └─ test_metrics.json
```

已整理出的汇总文件保存在：

```text
faceshield_outputs/summary/
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
| learning rate | 0.001 |
| weight decay | 0.0001 |
| dropout | 0.3 |
| early stopping patience | 8 |

## 3. 模型对比

| 模型 | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 14 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 |
| fusion_fft | 15 | 0.7678 | 0.6941 | 0.7617 | 0.6881 | 0.7083 | 0.6980 | 0.9340 |

## 4. 结果分析

从测试集结果看，RGB baseline 的整体表现优于当前 FFT 特征级融合模型。baseline 的 test AUC 为 0.8554，test F1 为 0.7973；fusion_fft 的 test AUC 为 0.7617，test F1 为 0.6980。

这说明当前轻量级 CNN 和小规模 FaceForensics++ 子集条件下，直接将 FFT 幅度谱作为第二分支并与 RGB 特征 concat，没有带来性能提升。可能原因包括：

1. FFT 幅度谱保留的是全局频域信息，局部伪造痕迹表达不足。
2. 当前频域分支较浅，学习到的高频伪影特征不够稳定。
3. 简单 concat 融合无法判断 RGB 特征与频域特征在不同样本中的可靠性。
4. 训练集规模偏小，增加频域分支后模型参数量增大，更容易过拟合。

因此，当前系统实现阶段可以优先使用 baseline 作为可部署主模型，将 fusion_fft 作为频域-空域融合探索实验。论文或答辩中应如实说明：本项目完成了频域-空域融合结构设计和实验验证，但初版 FFT 融合模型未超过 RGB baseline，后续需要继续优化频域特征构建和融合策略。

## 5. 后续改进方向

1. 频域特征从全图 FFT 幅度谱改为高频区域裁剪、环形频带统计或多尺度 FFT。
2. 增加 DCT 或 block-DCT 特征，更贴近 JPEG 压缩和局部伪影。
3. 使用 attention 或 gating fusion 替代简单 concat，让模型动态调整 RGB 与频域特征权重。
4. 将 backbone 从轻量 CNN 升级为 ResNet18、MobileNetV3 或 EfficientNet，并加入更强正则化。
5. 扩展 fake 类型到 Face2Face、FaceSwap 和 NeuralTextures，验证跨伪造方法泛化能力。
