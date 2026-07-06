# 本轮训练论文素材记录

更新时间：2026-07-06

本文档用于记录本轮 FaceShield 算法训练中可以写入课程论文/项目报告的内容。记录依据来自 `training/` 训练代码、`data/ffpp_faces/face_manifest_clean.csv` 数据清单，以及 `model/` 中的训练输出。

## 1. 可写入论文的内容总览

| 论文位置 | 建议写入内容 | 本轮证据 |
|---|---|---|
| 数据集与预处理 | 使用 FaceForensics++ c23 中 `original` 与 `Deepfakes` 两类视频，抽帧后进行人脸检测、裁剪和 224x224 归一化输入 | `data/ffpp_faces/face_manifest_clean.csv`、`docs/algorithm_design.md` |
| 模型方法 | 对比 RGB 单分支 baseline、初版 FFT concat 融合模型 fusion_fft，以及优化后的高频 FFT 门控融合模型 fusion_v2 | `training/models.py`、`training/dataset.py` |
| 训练设置 | PaddlePaddle 2.4.0，GPU 训练，AdamW，batch size 32，dropout 0.3，early stopping patience 8；baseline/fusion_fft 使用 lr=0.001，fusion_v2 主配置使用 lr=0.0005 | `model/outputs/*/config.json`、`training/train.py` |
| 评价指标 | Accuracy、AUC、Precision、Recall、F1、Loss；以验证集 AUC 选择最佳 checkpoint | `training/metrics.py`、`training/train.py` |
| 实验结果 | 初版 fusion_fft 明显弱于 baseline；优化后的 fusion_v2 在三组 seed 平均 AUC、Accuracy、F1 上略优于 baseline，当前推荐作为频域-空域融合主结果 | `model/summary/metrics_summary.csv`、AutoDL 训练输出 |
| 结果分析 | 初版 FFT 融合失败主要与全局 FFT 表达和简单 concat 融合有关；fusion_v2 通过高频 FFT、spatial checkpoint 初始化和 gating fusion 改善了效果，但不同 seed 之间仍有波动 | `model/summary/experiment_summary.md`、AutoDL 训练输出 |
| 后续改进 | 引入 DCT/block-DCT、多尺度高频特征、attention/gating 融合、更强 backbone 和更多伪造类型 | `docs/algorithm_design.md`、本轮结果分析 |

## 2. 数据集与预处理可写内容

本轮训练使用 FaceForensics++ c23 子集，其中真实样本来自 `original`，伪造样本来自 `Deepfakes`。视频数据不直接进入模型，而是先抽帧，再进行人脸区域检测、裁剪和 resize，最终得到图片级人脸裁剪样本。标签约定为：

| 类别 | 标签 | 含义 |
|---|---:|---|
| real | 0 | 原始真实人脸图片 |
| fake | 1 | Deepfakes 伪造人脸图片 |

当前训练使用 `face_manifest_clean.csv`，样本划分如下：

| split | real | fake | total | unique videos |
|---|---:|---:|---:|---:|
| train | 1887 | 1882 | 3769 | 148 |
| val | 644 | 640 | 1284 | 48 |
| test | 547 | 545 | 1092 | 44 |
| total | 3078 | 3067 | 6145 | 240 |

数据集整体较均衡，real 与 fake 数量接近 1:1，因此 Accuracy、F1 与 AUC 都具有参考价值。当前 clean manifest 中自动检测到人脸的样本为 6144 张，保留中心裁剪回退样本 1 张；论文中可以写“主要使用自动人脸检测裁剪结果，并对异常样本进行清洗”，不建议写成“全部样本均成功检测到人脸”。

可直接写入论文的表述：

> 本项目采用 FaceForensics++ c23 压缩视频子集构建图片级伪造人脸检测数据。真实样本来自 original 序列，伪造样本来自 Deepfakes 序列。由于系统目标是对单张图片或视频帧进行伪造检测，本文将视频数据按固定间隔抽帧，并对每一帧进行人脸检测和裁剪，统一 resize 为 224x224 后输入模型。训练、验证和测试集分别包含 3769、1284 和 1092 张人脸裁剪图，真假样本比例接近 1:1。

## 3. 模型方法可写内容

### 3.1 RGB baseline

baseline 是单路 RGB 图片分类模型，输入为 3 通道人脸裁剪图。模型使用轻量 CNN backbone 提取空间域纹理与结构特征，经过全局平均池化和全连接分类器输出 real/fake 二分类结果。

结构摘要：

```text
RGB face crop
-> TinyBackbone(in_channels=3, feature_dim=128)
-> AdaptiveAvgPool2D
-> Dropout(0.3)
-> Linear(128, 2)
-> real/fake logits
```

baseline 的论文作用是建立可比较基线，用于判断频域特征是否真正带来收益。

### 3.2 频域-空域融合模型 fusion_fft

fusion_fft 是本轮实验的频域-空域融合探索模型。它包含两个分支：

| 分支 | 输入 | 作用 |
|---|---|---|
| spatial branch | RGB 人脸裁剪图 | 学习颜色、纹理、局部结构等空间域线索 |
| frequency branch | 单通道 FFT 幅度谱 | 学习高频伪影、压缩残留和频域异常 |

FFT 输入构建流程：

```text
RGB face crop
-> grayscale
-> fft2
-> fftshift
-> log(1 + abs(spectrum))
-> min-max normalize
-> 1-channel FFT tensor
```

fusion_fft 的结构摘要：

```text
RGB face crop -> TinyBackbone(3 channels) -> spatial feature
FFT spectrum  -> TinyBackbone(1 channel) -> frequency feature

concat(spatial feature, frequency feature)
-> Dropout(0.3)
-> Linear(256, 128)
-> ReLU
-> Dropout(0.3)
-> Linear(128, 2)
-> real/fake logits
```

可直接写入论文的表述：

> 为了探索伪造人脸在频域中的异常特征，本文设计了频域-空域融合模型。该模型一方面使用 RGB 分支提取人脸图像中的空间纹理和结构特征，另一方面将人脸灰度图转换为 FFT 幅度谱，并使用频域分支提取频谱特征。两个分支的输出特征在分类头前进行拼接融合，最后通过全连接层输出伪造概率。该设计用于验证频域信息是否能够补充 RGB 空域特征。

### 3.3 优化后的频域-空域融合模型 fusion_v2

由于初版 fusion_fft 使用全局 FFT 幅度谱和简单 concat 融合，测试效果低于 RGB baseline，后续对融合模型进行了三点优化：

| 优化点 | 设计 | 目的 |
|---|---|---|
| 高频 FFT 输入 | 对 FFT 幅度谱抑制中心低频区域，仅保留高频区域 | 强化伪造边界、纹理异常和压缩残留等高频线索 |
| spatial checkpoint 初始化 | 使用已训练 baseline checkpoint 初始化 RGB 空域分支 | 避免双分支从零训练导致空域特征不稳定 |
| gating residual fusion | 用门控机制控制频域特征注入空间特征的强度 | 替代简单 concat，使模型自适应选择频域补充信息 |

fusion_v2 的结构摘要：

```text
RGB face crop
-> spatial branch initialized from baseline checkpoint
-> spatial feature

RGB face crop
-> grayscale
-> FFT magnitude
-> suppress low-frequency center region
-> high-frequency FFT tensor
-> frequency branch
-> frequency feature

gate = sigmoid(MLP(concat(spatial feature, frequency feature)))
fused feature = spatial feature + gate * transformed frequency feature
-> classifier
-> real/fake logits
```

可直接写入论文的表述：

> 针对初版 FFT 融合模型效果不稳定的问题，本文进一步设计了 fusion_v2 结构。该模型保留 RGB 空域分支作为主干，并使用 baseline 训练权重初始化该分支；频域分支不再使用完整 FFT 幅度谱，而是抑制低频中心区域，仅保留更可能包含伪造痕迹的高频频谱信息。在融合阶段，模型通过门控残差结构控制频域特征对空域特征的补充强度，从而缓解简单拼接带来的特征干扰问题。

## 4. 训练设置可写内容

| 项目 | 设置 |
|---|---|
| 框架 | PaddlePaddle 2.4.0 |
| 设备 | GPU `gpu:0` |
| 输入尺寸 | 224x224 |
| batch size | 32 |
| 最大 epoch | 30 |
| optimizer | AdamW |
| learning rate | 0.001 |
| weight decay | 0.0001 |
| dropout | 0.3 |
| feature dim | 128 |
| random seed | 42 |
| 数据增强 | 训练集随机水平翻转、亮度/对比度/颜色扰动 |
| best checkpoint 选择 | 验证集 AUC 最高 |
| early stopping patience | 8 |

两组实验使用完全相同的数据划分和训练超参数，只改变模型结构，便于公平比较。

可直接写入论文的表述：

> 训练过程中采用 AdamW 优化器，初始学习率设置为 0.001，weight decay 为 0.0001，batch size 为 32。为了减轻过拟合，分类头中加入 dropout，并对训练集样本进行随机水平翻转和轻量颜色扰动。模型训练最多 30 个 epoch，并以验证集 AUC 作为最佳模型选择标准；当验证集 AUC 连续 8 个 epoch 未提升时触发 early stopping。

## 5. 本轮实验结果

### 5.1 初版 baseline 与 fusion_fft 对比

| 模型 | best epoch | 实际训练轮数 | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss | 训练耗时 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 14 | 22 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 | 426.66s |
| fusion_fft | 15 | 23 | 0.7678 | 0.6941 | 0.7617 | 0.6881 | 0.7083 | 0.6980 | 0.9340 | 681.53s |

baseline 相比 fusion_fft 的测试集提升：

| 指标 | baseline - fusion_fft |
|---|---:|
| Accuracy | +8.70 个百分点 |
| AUC | +9.37 个百分点 |
| Precision | +5.33 个百分点 |
| Recall | +15.41 个百分点 |
| F1 | +9.93 个百分点 |

fusion_fft 训练耗时比 baseline 多 254.87 秒，约增加 59.74%。在当前小规模数据和轻量 CNN 结构下，加入 FFT 分支并未提升性能，反而降低了准确率、AUC 和 F1。

可直接写入论文的结果分析：

> 从实验结果看，RGB baseline 在本轮测试集上取得了 0.7811 的 Accuracy、0.8554 的 AUC 和 0.7973 的 F1，整体优于频域-空域融合模型。fusion_fft 的 test AUC 为 0.7617，F1 为 0.6980，说明当前直接使用全局 FFT 幅度谱并进行特征拼接，尚未有效提升模型对 Deepfakes 伪造样本的判别能力。可能原因包括：全局 FFT 对局部伪造痕迹表达不足，简单 concat 融合无法自适应区分 RGB 特征和频域特征的重要性，同时双分支结构增加了模型参数量，在当前训练集规模下更容易产生过拟合。

### 5.2 fusion_v2 优化实验

主配置：

```bash
python training/train.py \
  --data-root data/ffpp_faces \
  --manifest face_manifest_clean.csv \
  --model fusion_v2 \
  --output-dir outputs/fusion_v2_seedX \
  --device gpu \
  --epochs 30 \
  --batch-size 32 \
  --lr 5e-4 \
  --seed X \
  --spatial-checkpoint outputs/baseline/best.pdparams \
  --freeze-spatial-epochs 3
```

单次结果：

| 模型 | seed | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss | 训练耗时 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 42 | 14 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 | 426.66s |
| baseline | 7 | 28 | 0.8552 | 0.7866 | 0.8786 | 0.7727 | 0.8110 | 0.7914 | 0.7825 | 605.40s |
| baseline | 123 | 16 | 0.8589 | 0.8223 | 0.9074 | 0.8343 | 0.8037 | 0.8187 | 0.4803 | 514.77s |
| fusion_v2 | 42 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.7719 | 713.61s |
| fusion_v2 | 7 | 2 | 0.8446 | 0.7821 | 0.8632 | 0.7902 | 0.7670 | 0.7784 | 0.8182 | 327.86s |
| fusion_v2 | 123 | 5 | 0.8627 | 0.8013 | 0.8948 | 0.7706 | 0.8569 | 0.8115 | 0.7485 | 388.70s |

三组 seed 平均结果：

| 模型 | Accuracy | AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|
| baseline 平均 | 0.7967 | 0.8805 | 0.7828 | 0.8257 | 0.8025 | 0.6318 |
| fusion_v2 平均 | 0.8056 | 0.8865 | 0.7956 | 0.8226 | 0.8082 | 0.7795 |
| fusion_v2 - baseline | +0.0089 | +0.0060 | +0.0128 | -0.0031 | +0.0058 | +0.1477 |

结果解读：

- fusion_v2 相比 baseline 的三 seed 平均 AUC 提升 0.0060，Accuracy 提升 0.0089，F1 提升 0.0058，说明优化后的频域-空域融合方案带来了一定增益。
- 提升幅度较小，且按相同 seed 对比时，fusion_v2 只在 seed42 明显优于 baseline，seed7 和 seed123 不占优，因此不能表述为“显著提升”。
- fusion_v2 的平均 Recall 略低于 baseline，说明在部分随机种子下仍存在 fake 漏检风险，后续需要继续优化频域分支和融合稳定性。

可直接写入论文的结果分析：

> 初版 fusion_fft 未能超过 RGB baseline 后，本文进一步采用高频 FFT 输入、baseline checkpoint 初始化和门控残差融合构建 fusion_v2。三组随机种子的实验结果显示，fusion_v2 的平均 test AUC 为 0.8865，平均 Accuracy 为 0.8056，平均 F1 为 0.8082，均略高于 RGB baseline 的 0.8805、0.7967 和 0.8025。该结果说明频域高频信息在经过更合理的特征构建和融合策略后，能够对空域特征形成一定补充。但由于不同随机种子下结果仍有波动，本文仅将其表述为“一定提升”，不夸大为显著提升。

### 5.3 调参记录与最终选择

在 fusion_v2 主配置基础上，进一步尝试了降低学习率和调整 spatial branch 冻结轮数：

| 配置 | seed | freeze-spatial-epochs | lr | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss | 判断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 主配置 | 42 | 3 | 5e-4 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.7719 | 当前最佳 seed42 fusion 配置 |
| 配置 A | 42 | 0 | 3e-4 | 1 | 0.8595 | 0.8022 | 0.8718 | 0.8270 | 0.7633 | 0.7939 | 0.6372 | 不冻结会扰动已训练空域分支，整体退步 |
| 配置 B | 42 | 1 | 3e-4 | 22 | 0.8681 | 0.7912 | 0.8940 | 0.8499 | 0.7064 | 0.7715 | 1.1277 | Recall 和 F1 偏低，fake 漏检风险较高 |
| 配置 C | 42 | 3 | 3e-4 | 14 | 0.8616 | 0.7958 | 0.8887 | 0.8286 | 0.7450 | 0.7845 | 0.9445 | 降低学习率未提升稳定性 |

调参结论：

- 当前最适合作为论文主结果的配置是 `fusion_v2 + spatial checkpoint + freeze 3 epochs + lr=5e-4`。
- `lr=3e-4` 在三种冻结策略下均未超过主配置，因此暂不继续沿学习率方向小幅调参。
- 对“AI 换脸诈骗检测”场景，Recall 过低意味着 fake 漏检风险更高，因此配置 B 虽然 AUC 接近主配置，但不适合作为最终模型。
- 后续更有价值的优化方向不是继续微调 lr，而是改进频域特征表达、融合结构和 backbone。

## 6. 论文中建议采用的结论口径

推荐写法：

> 本项目完成了 RGB 空域 baseline、初版 FFT concat 融合模型以及优化后的 fusion_v2 频域-空域融合模型。实验结果表明，初版 fusion_fft 由于采用全局 FFT 幅度谱和简单特征拼接，测试效果低于 RGB baseline；在此基础上，fusion_v2 通过高频 FFT 输入、baseline checkpoint 初始化和门控残差融合，使三组随机种子的平均 AUC、Accuracy 和 F1 相比 baseline 均有一定提升。当前系统可采用 fusion_v2 作为频域-空域融合主模型，同时保留 baseline 作为对照模型。由于 fusion_v2 在不同 seed 下仍存在波动，后续仍需从频域特征构建、融合策略和模型 backbone 等方面继续优化。

不建议写法：

- 不建议写“频域-空域融合显著提升了检测准确率”，因为 fusion_v2 只是平均略优于 baseline，提升幅度较小且存在 seed 波动。
- 不建议写“系统已经具备视频级检测能力”，当前训练和模型评估是图片级/帧级检测。
- 不建议写“覆盖所有 Deepfake 类型”，当前训练只使用 `original` 与 `Deepfakes` 两类，尚未覆盖 Face2Face、FaceSwap、NeuralTextures 等方法。
- 不建议写“全部样本均自动检测成功”，当前 clean manifest 中仍保留 1 个回退样本。

## 7. 可放入论文的图表

| 图表 | 建议标题 | 数据来源 |
|---|---|---|
| 数据集划分表 | FaceForensics++ 子集样本划分统计 | `data/ffpp_faces/face_manifest_clean.csv` |
| 模型结构图 | 频域-空域融合模型结构 | 可根据 `training/models.py` 绘制 |
| 训练曲线图 | baseline、fusion_fft、fusion_v2 验证集 AUC/Accuracy 曲线 | `model/summary/training_curves.svg`、AutoDL 输出 |
| 指标对比表 | 不同模型在测试集上的检测性能对比 | `model/summary/metrics_summary.csv`、AutoDL 输出 |
| 消融分析表 | RGB baseline、初版 FFT concat、fusion_v2 gating 融合对比 | 同上 |

建议论文正文优先放“数据集划分表”和“指标对比表”。训练曲线可以放在实验分析小节，用来说明 early stopping 和模型收敛情况。

## 8. 后续改进方向可写内容

本轮实验的后续优化可以写在“总结与展望”或“系统不足”部分：

1. 频域特征方面，在当前高频 FFT 的基础上继续尝试环形频带统计、多尺度 FFT 或 block-DCT，以增强局部伪造痕迹表达。
2. 融合策略方面，在当前 gating fusion 的基础上继续尝试 attention 或 cross-modal interaction，让模型更稳定地调整 RGB 与频域特征权重。
3. Backbone 方面，将轻量 CNN 替换为 ResNet18、MobileNetV3 或 EfficientNet，并比较准确率、参数量和推理耗时。
4. 数据集方面，扩展 FaceForensics++ 中 Face2Face、FaceSwap、NeuralTextures 等伪造类型，验证跨伪造方法泛化能力。
5. 鲁棒性方面，增加 JPEG 压缩、缩放、模糊、截图转发等扰动测试，更贴近真实互联网传播场景。

## 9. 证据文件索引

| 文件 | 用途 |
|---|---|
| `training/dataset.py` | 数据读取、RGB 归一化、完整 FFT 幅度谱和高频 FFT 输入生成、数据增强 |
| `training/models.py` | baseline、fusion_fft 与 fusion_v2 模型结构 |
| `training/metrics.py` | Accuracy、AUC、Precision、Recall、F1 计算逻辑 |
| `training/train.py` | 训练流程、AdamW、early stopping、best checkpoint 选择 |
| `training/README.md` | AutoDL 训练命令和输出文件说明 |
| `model/outputs/baseline/config.json` | baseline 训练配置 |
| `model/outputs/fusion_fft/config.json` | fusion_fft 训练配置 |
| `model/outputs/fusion_v2_seed*/config.json` | fusion_v2 训练配置 |
| `model/outputs/*/best_metrics.json` | 最佳验证集指标 |
| `model/outputs/*/test_metrics.json` | 测试集最终指标 |
| `model/summary/metrics_summary.csv` | 论文指标表来源 |
| `model/summary/epoch_history.csv` | 训练曲线数据来源 |
| `model/summary/training_curves.svg` | 训练曲线图 |
| `docs/experiment_results.md` | 已整理的简版实验结果 |
