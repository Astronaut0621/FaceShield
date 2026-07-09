# 跨域泛化实验方案

本文档记录 FaceShield 当前跨域实验的执行方案。跨域实验的目的不是重新训练模型，而是用已经训练好的 `fusion_v2` 检查模型在训练域之外的表现。

## 1. 方案 A：FaceForensics++ 跨伪造类型

实验思路：训练集仍然是 `original + Deepfakes`，测试集换成 `original + FaceSwap` 或 `original + Face2Face`。这样可以观察模型是否只记住了 Deepfakes 的伪影，还是能泛化到其他换脸方法。

推荐先跑 FaceSwap：

```powershell
D:\Anaconda\python.exe tools\download-FaceForensics.py data\FaceForensics-data -d FaceSwap -c c23 -t videos -n 120 --server EU2
```

抽帧：

```powershell
.\.venv\Scripts\python.exe tools\extract_ffpp_frames.py `
  --fake-method FaceSwap `
  --output-dir data\ffpp_frames_faceswap `
  --compression c23 `
  --frame-interval 20
```

人脸裁剪：

```powershell
.\.venv\Scripts\python.exe tools\extract_faces.py `
  --input-manifest data\ffpp_frames_faceswap\manifest.csv `
  --frames-root data\ffpp_frames_faceswap `
  --output-dir data\ffpp_faces_faceswap
```

评估已部署的 `fusion_v2`：

```powershell
.\.venv\Scripts\python.exe training\evaluate_cross_domain.py `
  --data-root data\ffpp_faces_faceswap `
  --manifest face_manifest.csv `
  --split test `
  --domain-name ffpp_faceswap `
  --model-dir model\deploy\fusion_v2 `
  --output-dir model\cross_domain\ffpp_faceswap `
  --device cpu
```

如果要换成 Face2Face，只需要把下载和抽帧命令里的 `FaceSwap` 改成 `Face2Face`，并把输出目录改成 `ffpp_frames_face2face`、`ffpp_faces_face2face`、`ffpp_face2face`。

## 2. 方案 B：Celeb-DF v2 跨数据集

实验思路：使用 Celeb-DF v2 的真实视频和伪造视频构造测试集，直接评估 `fusion_v2`。这属于真正的 cross-dataset 测试，比方案 A 更严格。

假设数据集解压到：

```text
data/Celeb-DF-v2/
├─ Celeb-real/
├─ YouTube-real/
├─ Celeb-synthesis/
└─ List_of_testing_videos.txt
```

抽帧：

```powershell
.\.venv\Scripts\python.exe tools\extract_celebdf_frames.py `
  --dataset-root data\Celeb-DF-v2 `
  --output-dir data\celebdf_frames `
  --frame-interval 20
```

人脸裁剪：

```powershell
.\.venv\Scripts\python.exe tools\extract_faces.py `
  --input-manifest data\celebdf_frames\manifest.csv `
  --frames-root data\celebdf_frames `
  --output-dir data\celebdf_faces
```

评估：

```powershell
.\.venv\Scripts\python.exe training\evaluate_cross_domain.py `
  --data-root data\celebdf_faces `
  --manifest face_manifest.csv `
  --split test `
  --domain-name celebdf_v2 `
  --model-dir model\deploy\fusion_v2 `
  --output-dir model\cross_domain\celebdf_v2 `
  --device cpu
```

## 3. 输出文件

`training/evaluate_cross_domain.py` 会生成：

```text
model/cross_domain/<run>/
├─ metrics.json
├─ metrics.csv
├─ group_summary.csv
├─ predictions.csv
└─ summary.md
```

其中：

- `metrics.csv`：整体 Accuracy、AUC、Precision、Recall、F1、FP、FN。
- `group_summary.csv`：按 real/fake 和 method 分组的平均伪造概率、预测为 fake 的比例和正确率。
- `predictions.csv`：每张图片的 fake probability 和预测结果，便于抽样人工检查。
- `summary.md`：可以直接放入实验记录或论文草稿的简表。

## 4. 论文表述口径

如果方案 A 或 B 指标下降，这是正常现象，不能写成失败。更合理的表述是：

> 为验证模型的泛化能力，本文进一步使用未参与训练的伪造类型或外部数据集进行跨域测试。该实验不重新训练模型，仅替换测试数据。若模型性能相比同域测试下降，说明当前模型仍部分依赖 Deepfakes 数据中的特定伪影，后续需要通过更多伪造类型联合训练、频域数据增强、对比学习或更强 backbone 提升泛化能力。

## 5. FaceSwap 已完成结果

本轮已完成 FaceForensics++ `FaceSwap` 子集下载、抽帧、人脸裁剪和跨伪造类型评估。

数据检查：

| 项目 | 数量 |
| --- | ---: |
| FaceSwap 视频 | 120 |
| 抽帧图片 | 5666 |
| 人脸裁剪图片 | 5666 |
| 检测到人脸 | 5631 |
| fallback 中心裁剪 | 35 |
| 裁剪错误 | 0 |

测试集分布：

| split | real | fake |
| --- | ---: | ---: |
| train | 1925 | 1484 |
| val | 652 | 508 |
| test | 611 | 486 |

跨伪造类型评估结果：

| 模型 | 测试域 | 样本数 | Accuracy | AUC | Precision | Recall | F1 | TP | FP | TN | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | original + FaceSwap | 1097 | 0.5068 | 0.4841 | 0.4311 | 0.3539 | 0.3887 | 172 | 227 | 384 | 314 |
| fusion_v2 | original + FaceSwap | 1097 | 0.5077 | 0.4492 | 0.3911 | 0.1996 | 0.2643 | 97 | 151 | 460 | 389 |
| fusion_v2 no fallback | original + FaceSwap | 1085 | 0.5115 | 0.4533 | 0.4008 | 0.2012 | 0.2680 | 97 | 145 | 458 | 385 |

结果分析：

1. `fusion_v2` 在同域 Deepfakes 测试上 AUC 为 0.9014，但跨到 FaceSwap 后 AUC 下降到 0.4492，说明当前模型存在明显跨伪造类型泛化不足。
2. 排除 fallback 裁剪后，`fusion_v2` AUC 从 0.4492 变为 0.4533，F1 从 0.2643 变为 0.2680，变化很小，说明主要问题不是裁剪失败造成的。
3. baseline 也下降到 AUC 0.4841、F1 0.3887，说明只用 `original + Deepfakes` 训练时，模型整体容易学习 Deepfakes 特有伪影，对 FaceSwap 伪影识别不足。
4. `fusion_v2` 对 FaceSwap fake 的平均伪造概率只有 0.2067，fake 召回率只有 0.1996，说明它倾向于把 FaceSwap 判为 real。后续如果要提升泛化能力，应加入 FaceSwap/Face2Face 联合训练，或做跨伪造类型数据增强和对比学习。

论文中可以将该实验写成“泛化性验证实验”或“跨伪造类型实验”。不应写成当前模型已经具备强跨域泛化能力，而应写成发现了当前模型的局限，并据此提出后续改进方向。
