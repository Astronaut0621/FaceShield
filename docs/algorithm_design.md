# FaceShield 算法设计

## 1. 任务定义

FaceShield 的算法任务是图片级伪造人脸二分类。系统使用阶段只输入一张待检测图片，经过人脸裁剪和图像预处理后，模型输出 real/fake 判断结果、伪造概率和可解释性热力图。

标签定义如下：

| 类别 | 标签 | 含义 |
|---|---:|---|
| real | 0 | 原始真实人脸图片 |
| fake | 1 | 经过 DeepFake 等方法伪造的人脸图片 |

训练阶段使用 real 图片和 fake 图片两类样本监督模型学习伪造特征；推理阶段不需要提供原图作为对照，只需上传一张可疑图片。本项目当前不做双图比对，也不做视频级时序建模。视频数据只作为图片数据来源，通过抽帧转换为图片级训练样本。

## 2. 数据集设计

当前采用 FaceForensics++ c23 压缩视频子集，下载范围为 `original` 和 `Deepfakes` 两类：

- `original_sequences/youtube/c23/videos` 作为 real 数据来源。
- `manipulated_sequences/Deepfakes/c23/videos` 作为 fake 数据来源。

抽帧策略：

- 使用官方 `train.json`、`val.json`、`test.json` 按视频 ID 继承训练集、验证集和测试集划分。
- 每隔 20 帧抽取一张图片，降低相邻帧重复。
- 保存 `manifest.csv`，记录 split、label、source video 和 image path。

当前已生成图片数据：

| split | real | fake | total |
|---|---:|---:|---:|
| train | 1925 | 1925 | 3850 |
| val | 652 | 652 | 1304 |
| test | 611 | 611 | 1222 |
| total | 3188 | 3188 | 6376 |

## 3. 人脸裁剪预处理

训练和推理主路径都使用人脸裁剪图，而不是完整帧。完整帧中包含背景、台标、字幕、会议室等非人脸信息，直接训练容易导致模型学习到背景偏差，而不是伪造人脸痕迹。

人脸裁剪流程：

```text
输入图片
-> OpenCV Haar Cascade 人脸检测
-> 选择面积最大的人脸框
-> 人脸框扩大 1.3 倍，保留脸部边缘和融合边界
-> 裁剪为正方形
-> resize 到 224x224
-> 检测失败时回退到中心裁剪
```

OpenCV Haar Cascade 只用于裁剪预处理，不负责判断真假。最终 real/fake 分类模型使用 PaddlePaddle 实现。

当前已生成裁剪后人脸数据：

| 文件 | 说明 | 样本数 |
|---|---|---:|
| `data/ffpp_faces/face_manifest.csv` | 全部裁剪结果，包含检测失败后的中心裁剪回退样本 | 6376 |
| `data/ffpp_faces/face_manifest_detected.csv` | 仅保留自动检测到人脸的样本，推荐用于训练 | 6338 |
| `data/ffpp_faces/face_manifest_clean.csv` | 排除中心裁剪回退、无眼部特征疑似坏样本和人工标记坏样本，优先用于训练 | 6145 |
| `data/ffpp_faces/face_manifest_review_moved.csv` | 已移入 `data/ffpp_faces/review` 的问题候选样本 | 231 |

检测统计：

| 项目 | 数量 |
|---|---:|
| 自动检测到人脸 | 6338 |
| 中心裁剪回退 | 38 |
| 读取或保存错误 | 0 |

推荐训练阶段优先使用 `face_manifest_clean.csv`，避免中心裁剪回退和明显非人脸误检样本进入训练集。系统推理阶段仍保留中心裁剪回退机制，用于处理检测不到人脸的异常输入。

## 4. 总体算法路线

算法采用先 baseline、后融合模型的实现顺序：

1. RGB baseline：使用单路 CNN 对人脸裁剪图进行 real/fake 二分类。
2. 频域输入构建：对人脸裁剪图计算 FFT 幅度谱，DCT 作为后续可选扩展。
3. 频域-空域融合：采用双分支特征级融合，空域分支学习 RGB 纹理与局部结构，频域分支学习高频伪影和压缩残留。
4. 可解释性：对最终分类结果生成 Grad-CAM 热力图，展示模型关注的人脸区域。

FFT 频域输入构建流程：

```text
face crop RGB
-> grayscale
-> np.fft.fft2
-> np.fft.fftshift
-> log(1 + abs(spectrum))
-> min-max normalize
-> resize / stack 为模型可读取的频域特征图
```

后续如果时间允许，可增加 DCT 分支或 FFT/DCT 对比实验。DCT 更贴近 JPEG 压缩块特征，适合分析压缩伪影；FFT 更适合 MVP 阶段快速构建全局频域特征。

频域-空域融合结构：

```text
RGB face crop -> spatial CNN -> spatial feature
FFT spectrum  -> frequency CNN -> frequency feature

spatial feature + frequency feature
-> concat
-> fully connected classifier
-> real/fake probability
```

采用特征级融合而不是输入级融合或决策级融合，是为了让两个分支分别学习不同类型的伪造线索，同时保持模型是一个端到端二分类网络。

## 5. 模型结构设计

当前数据规模较小，MVP 阶段优先采用轻量 backbone，保证模型可以稳定训练、快速推理，并能接入后端系统。

### 5.1 Baseline 模型

Baseline 使用单空域分支进行 real/fake 二分类：

```text
RGB face crop
-> lightweight CNN / MobileNetV3-Small / ResNet18
-> global average pooling
-> fully connected classifier
-> fake probability
```

Baseline 的作用是建立可对比基线，用于证明频域分支是否带来提升。

### 5.2 频域-空域融合模型

MVP 融合模型采用双分支轻量结构：

```text
Spatial branch:
RGB face crop -> lightweight CNN -> spatial feature

Frequency branch:
FFT spectrum -> shallow CNN -> frequency feature

Fusion head:
concat(spatial feature, frequency feature)
-> dropout
-> linear classifier
-> fake probability
```

频域分支不使用过深网络，避免在小规模数据上过拟合。空域分支可优先使用 PaddlePaddle 内置或自定义轻量 CNN，后续根据训练效果替换为更强 backbone。

### 5.3 后续改进方向

1. **Backbone 升级**：将轻量 CNN 替换为 ResNet18、MobileNetV3 或 EfficientNet，并对比参数量、推理速度和准确率。
2. **频域特征增强**：在 FFT 幅度谱基础上加入 DCT、局部 block-DCT 或高频能量图，用于捕捉 JPEG 压缩与局部伪影。
3. **数据集扩展**：从 `original + Deepfakes` 扩展到 Face2Face、FaceSwap、NeuralTextures 和 FaceShifter，提升对不同伪造方法的泛化能力。
4. **鲁棒性实验**：增加 JPEG 压缩、缩放、模糊等扰动测试，验证模型在真实网络传播场景下的稳定性。
5. **可解释性增强**：除 Grad-CAM 外，可尝试对频域分支生成频谱响应可视化，展示模型关注的高频异常区域。

## 6. 评价指标

模型评价采用 Accuracy 和 AUC 作为主指标，Precision、Recall 和 F1 作为辅助指标。

| 指标 | 含义 | 用途 |
|---|---|---|
| Accuracy | 分类正确样本占比 | 直观衡量整体二分类效果 |
| AUC | 不同阈值下模型区分 real/fake 的能力 | 衡量伪造概率排序质量 |
| Precision | 预测为 fake 的样本中真实 fake 的比例 | 控制误报 |
| Recall | fake 样本中被检测出的比例 | 控制漏报 |
| F1 | Precision 和 Recall 的调和平均 | 综合衡量检测效果 |

系统展示时使用 `fake_probability` 生成风险等级：

| fake_probability | risk level |
|---:|---|
| `< 0.4` | 低风险 |
| `0.4 - 0.7` | 中风险 |
| `>= 0.7` | 高风险 |

## 7. 训练脚本

训练代码位于 `training/`，上传 AutoDL 时只需要配合 `data/ffpp_faces` clean 数据使用。

| 文件 | 作用 |
|---|---|
| `training/dataset.py` | 读取 `face_manifest_clean.csv`，加载 224x224 人脸图，并按需生成 FFT 幅度谱 |
| `training/models.py` | 定义 `baseline` 单分支 CNN 和 `fusion_fft` 频域-空域双分支模型 |
| `training/metrics.py` | 计算 Accuracy、AUC、Precision、Recall 和 F1 |
| `training/train.py` | 训练入口，支持 early stopping、保存 best checkpoint 和 test 评估 |
| `training/predict.py` | 单图预测入口，用于训练后快速检查 fake probability |
| `training/requirements-autodl.txt` | AutoDL 额外依赖，不包含 PaddlePaddle 本体 |

推荐先训练 baseline，再训练 fusion_fft：

```bash
python training/train.py --data-root data/ffpp_faces --manifest face_manifest_clean.csv --model baseline --output-dir outputs/baseline --device gpu
python training/train.py --data-root data/ffpp_faces --manifest face_manifest_clean.csv --model fusion_fft --output-dir outputs/fusion_fft --device gpu
```

两个模型使用同一份 clean 数据，便于比较频域分支是否带来提升。

## 8. 设计边界

- 本阶段只做图片级检测，不做视频级投票或时序建模。
- 系统主输入是一张待检测图片，不要求用户同时上传原图和换脸图。
- 视频上传检测作为后续扩展，不进入 MVP 主流程。
- 本阶段只使用 `original` 和 `Deepfakes`，后续可扩展到 Face2Face、FaceSwap、NeuralTextures 和 FaceShifter。
- 人脸检测器是预处理组件，分类模型才是核心算法组件。
