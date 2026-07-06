# Grad-CAM 可视化热力图记录

更新时间：2026-07-06

本文档记录 FaceShield 的可解释性可视化实现。当前实现基于 Grad-CAM，对模型判定 `fake` 类时依赖较强的图像区域生成热力图，并叠加到输入人脸图上，用于展示模型关注区域。

## 1. 展示效果

热力图不是逐像素篡改掩码，也不是局部概率图。它表示模型在当前分类决策中更关注的区域：

| 展示项 | 含义 |
|---|---|
| input.jpg | 输入人脸裁剪图 |
| heatmap.jpg | Grad-CAM 伪彩色热力图，红/黄表示贡献较高区域 |
| overlay.jpg | 热力图叠加到原图后的展示图，适合前端和论文截图 |
| result.json | 分类概率、预测标签、风险等级和输出路径 |

当前默认解释 `fake` 类，即展示“哪些区域为 fake 判断提供了更强证据”。这样更符合 AI 换脸诈骗检测场景：即使图片最终判为 real，也能观察是否存在较弱的 fake 可疑区域。

## 2. 实现方式

脚本位置：

```text
training/gradcam.py
```

实现要点：

1. 加载 `model/deploy/fusion_v2` 或其他指定 checkpoint。
2. 对输入图片进行与推理一致的 224x224 resize 和 RGB 归一化。
3. 对 `fusion_v2` 这类双分支模型，同时计算 RGB 输入和频域输入。
4. 以 RGB spatial branch 的最后一层 feature map 作为 Grad-CAM 目标层。
5. 对 `fake` logit 反向传播，计算通道权重并生成 CAM。
6. 将 CAM resize 回输入图大小，生成 `heatmap.jpg` 和 `overlay.jpg`。

需要注意：频域分支仍参与最终分类分数，但热力图坐标来自 RGB 空域分支。这样可以把关注区域合理叠加回人脸图像，避免把 FFT/DCT 频谱坐标误解释为人脸空间位置。

## 3. 运行命令

以最终主模型 `fusion_v2` 为例：

```powershell
.\.venv\Scripts\python.exe training\gradcam.py `
  --image data\ffpp_faces\test\fake\035_036_000001.jpg `
  --checkpoint model\deploy\fusion_v2\best.pdparams `
  --config model\deploy\fusion_v2\config.json `
  --output-dir model\gradcam\fusion_v2_fake_demo `
  --target-class fake `
  --device cpu
```

输出文件：

```text
model/gradcam/fusion_v2_fake_demo/
├─ input.jpg
├─ heatmap.jpg
├─ overlay.jpg
└─ result.json
```

也可以对 real 样本生成 fake 类关注区域：

```powershell
.\.venv\Scripts\python.exe training\gradcam.py `
  --image data\ffpp_faces\test\real\035_000001.jpg `
  --checkpoint model\deploy\fusion_v2\best.pdparams `
  --config model\deploy\fusion_v2\config.json `
  --output-dir model\gradcam\fusion_v2_real_demo `
  --target-class fake `
  --device cpu
```

## 4. 已生成示例

| 示例 | 路径 | 预测结果 |
|---|---|---|
| fake 样本 | `model/gradcam/fusion_v2_fake_demo/overlay.jpg` | predicted=fake, fake_probability=0.9999, risk=high |
| real 样本 | `model/gradcam/fusion_v2_real_demo/overlay.jpg` | predicted=real, fake_probability=0.0015, risk=low |
| 联系图 | `model/gradcam/fusion_v2_demo_contact_sheet.jpg` | 同时展示 input、heatmap、overlay |

## 5. 论文可用表述

> 为增强系统检测结果的可解释性，本文引入 Grad-CAM 方法生成可疑区域热力图。系统以模型对 fake 类的输出作为目标分数，对 RGB 空域分支最后一层特征图进行反向传播，计算各通道对分类结果的贡献权重，并生成伪彩色热力图。热力图被叠加到输入人脸图像上，用于展示模型在进行伪造判别时更关注的局部区域。需要说明的是，该热力图反映的是模型关注区域，并不等同于精确篡改掩码，因此主要用于辅助解释检测结果和前端可视化展示。

## 6. 后续接入建议

1. 后端检测接口在保存预测结果时，同时保存 `overlay.jpg` 路径。
2. 前端展示原图、fake probability、risk level 和 overlay 热力图。
3. 历史记录中保存热力图路径，便于用户回看检测依据。
4. 对 false positive 和 false negative 样本单独生成热力图，用于论文中的错误案例分析。
