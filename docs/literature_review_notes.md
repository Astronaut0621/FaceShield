# FaceShield 文献阅读与算法调整记录

更新时间：2026-07-06

本文档整理 `docs/论文/` 中 3 篇论文对 FaceShield 算法设计的参考价值。结论先行：这些论文有明显参考价值，尤其是《基于频域和空域多特征融合的深度伪造检测方法》与当前项目题目高度一致，可以作为“频域-空域融合”设计的主要文献依据；《局部相似度异常的强泛化性伪造人脸检测》更适合作为后续泛化性和高频噪声特征优化依据；综述论文适合写引言、相关工作、数据集和评价指标。

## 1. 文献价值总览

| 论文 | 主要内容 | 对 FaceShield 的参考价值 | 建议用途 |
|---|---|---|---|
| 基于频域和空域多特征融合的深度伪造检测方法 | DCT 频域动态三频带、EfficientNet_B4 + Transformer 空域多尺度、Q-K-V 融合、Grad-CAM 可解释性 | 与项目题目最贴合，能支撑“频域-空域融合”的合理性，也能解释为什么简单 concat 不够 | 核心参考文献，写入算法设计、相关工作、后续改进 |
| 局部相似度异常的强泛化性伪造人脸检测 | SRMCP 多尺度高频噪声、LSP 局部相似度异常、多任务学习、跨伪造类型泛化 | 能解释泛化性问题，也说明高频噪声和局部边界异常是有效线索 | 后续优化依据，支撑 SRM/局部相似度/跨库测试方向 |
| 深度网络生成式伪造人脸检测方法研究综述 | 系统梳理图像级和视频级伪造检测方法、数据集、评价指标、泛化问题 | 适合写背景、方法分类、FaceForensics++ 选择原因、AUC 指标合理性 | 引言、相关工作、实验设置依据 |

## 2. 与当前模型的关系

当前 FaceShield 已实现：

```text
RGB spatial branch + high-frequency FFT branch + gated residual fusion
```

这不是完全盲目的设计，和文献方向是吻合的：

- 频域信息可以捕捉空域纹理中不明显的伪造伪影。
- 空域分支仍然是主干，负责学习 RGB 人脸纹理、局部结构和颜色异常。
- 频域分支更适合作为辅助信息，而不是完全替代 RGB 空域特征。
- 融合方式不应停留在简单 concat，门控或 attention 类融合更合理。
- Grad-CAM 或热力图可以作为可解释性补充，帮助展示模型关注区域。

但当前实现仍是课程项目级简化版：

| 文献中的成熟设计 | 当前实现 | 差距 |
|---|---|---|
| DCT 动态划分低/中/高 3 个频带 | 高频 FFT，固定抑制低频中心 | 频带选择不够自适应 |
| EfficientNet_B4 + Transformer 多尺度空域模块 | 轻量 CNN spatial branch | 空域表达能力较弱 |
| Q-K-V 跨域融合 | gated residual fusion | 融合机制较简单，但比 concat 合理 |
| SRMCP 多尺度高频噪声 | FFT 高频图 | 缺少可学习高通滤波和多尺度噪声提取 |
| 跨伪造类型和跨数据集泛化实验 | original + Deepfakes 子集 | 泛化性验证不足 |

因此论文中不能写成“提出了全新的频域-空域融合方法”，更合适的口径是：

> 参考深度伪造检测中频域特征与空域特征互补的研究思路，本文结合项目周期和部署需求，实现了一种轻量化频域-空域双分支检测模型。模型以 RGB 空域分支为主干，并引入高频 FFT 分支提取频域伪影，通过门控残差结构进行特征融合，从而验证频域信息对图片级伪造人脸检测的补充作用。

## 3. 对当前实验结果的解释

我们已有实验现象：

- 初版 `fusion_fft` 直接使用完整 FFT 幅度谱 + concat，效果明显差于 baseline。
- 优化后的 `fusion_v2` 使用高频 FFT + baseline spatial checkpoint + gated residual fusion，三 seed 平均略优于 baseline。
- `fusion_v2` 仍存在 seed 波动，不能夸大为显著提升。

这些现象能从文献中解释：

1. 完整频谱包含大量低频结构和无关信息，直接输入可能干扰分类。
2. 频域信息更适合作为空域信息的辅助模态，因此需要 gating、attention 或 Q-K-V 融合，而不是简单拼接。
3. 伪造痕迹往往是局部的，单纯全局 FFT 对局部边界、嘴鼻区域、压缩伪影表达不充分。
4. 泛化性是深度伪造检测的核心问题，只在 Deepfakes 上训练和测试，不能说明模型覆盖所有换脸诈骗场景。

## 4. 下一步优化优先级

不建议继续盲目调 learning rate。结合文献，下一步应按下面顺序做：

### 4.1 优先补 DCT 分支

原因：

- 第一篇核心论文使用 DCT 频域划分，和我们最开始讨论的 FFT/DCT 方向一致。
- DCT 更贴近 JPEG 压缩和局部频带伪影，适合真实网络传播图片。
- 可以作为 `fusion_v3`：RGB spatial branch + DCT/high-frequency branch + gated fusion。

建议 MVP 做法：

```text
RGB face crop
-> grayscale
-> DCT
-> remove low-frequency block or keep high-frequency block
-> normalize
-> frequency branch
```

不必一开始就实现论文里的动态三频带，先做固定 high-frequency DCT，后续再写“动态频带划分”为改进方向。

### 4.2 加压缩鲁棒性测试

原因：

- 文献都强调压缩会影响检测效果。
- FaceForensics++ 本身有 RAW/C23/C40 压缩等级，我们当前只用了 c23。
- 换脸诈骗图片很可能经过微信、短视频平台、截图等二次压缩。

建议先不重新训练，只在 test 图片上生成 JPEG quality 95/75/50 的扰动版本，测试模型 AUC/F1 是否下降。

### 4.3 扩展 FaceForensics++ 伪造类型

原因：

- 综述和第二篇都强调跨伪造方法泛化。
- 当前只用了 `original + Deepfakes`，覆盖面不够。

时间允许时，优先补：

```text
FaceSwap
Face2Face
NeuralTextures
```

即使每类只下载少量视频，也能在报告里写“初步验证跨伪造类型能力”。

### 4.4 Grad-CAM 可解释性

原因：

- 第一篇把 Grad-CAM 作为可解释性分析，展示模型关注鼻子、嘴巴等伪造区域。
- 我们系统需求里本来就有“可疑区域热力图”。

建议把 Grad-CAM 作为系统展示功能，不一定参与训练指标提升。

## 5. 报告写法建议

### 5.1 引言/研究背景

引用综述论文，写：

- AI 换脸诈骗、伪造视频/图片传播带来的安全问题。
- 伪造人脸检测方法包括图像级和视频级。
- 当前方法仍面临泛化能力、压缩鲁棒性和实际部署效率问题。

### 5.2 相关工作

可按综述分类：

1. 基于数字图像处理和残差/高频噪声的方法。
2. 基于 CNN/深层特征的方法。
3. 基于空间域局部异常的方法。
4. 基于频域-空域多特征融合的方法。
5. 视频级方法，如生理信号、身份信息、多模态、时空一致性。

然后说明本项目选择的是“图片级频域-空域融合检测”，因为项目面向上传图片和视频帧检测，先不做视频时序建模。

### 5.3 算法设计

可以写：

- 空域分支学习 RGB 人脸纹理和局部结构。
- 频域分支学习高频伪影和压缩残留。
- 初版 concat 融合效果不好，因此改为 gated residual fusion。
- 当前模型是轻量化实现，后续可升级到 DCT 动态频带、多尺度 Transformer 或 SRMCP。

### 5.4 实验分析

必须保持谨慎：

- 可以写 `fusion_v2` 三 seed 平均略优于 baseline。
- 不写“显著提升”。
- 解释初版 `fusion_fft` 失败原因时，可以借文献说明：频域信息需要选择有效频带，并通过更合理的融合方式接入。

## 6. 对项目方向的判断

这些论文说明我们现在的方向是成立的，但需要调整目标：

- 不要把项目包装成“发明一种全新算法”。
- 应该包装成“参考频域-空域融合研究，完成可部署的轻量化伪造人脸检测系统”。
- 算法创新点可以写成工程化改进：高频 FFT 输入、gated residual fusion、PaddlePaddle 推理部署、Grad-CAM 可解释性、检测记录留存。
- 后续优化方向要明确写 DCT、SRMCP、跨伪造类型、压缩鲁棒性和视频级时序建模。

当前阶段最实际的下一步：

1. 先把这 3 篇论文写进报告的“相关工作”和“算法设计依据”。
2. 保持 `fusion_v2` 作为当前主模型。
3. 如果还有训练时间，优先做 DCT 高频分支或 JPEG 压缩鲁棒性测试，而不是继续微调学习率。

## 7. 已落地的 DCT 优化方向

根据上述判断，代码中新增了 `fusion_v3` 作为 DCT 方向的中间版本：

```text
RGB spatial branch
+ fixed DCT low/mid/high frequency bands
+ gated residual fusion
-> real/fake classifier
```

需要注意：

- `fusion_v3` 不是完整复现论文中的动态三频带方法，而是固定低/中/高三频带的轻量化实现。
- `fusion_v3` 沿用 `fusion_v2` 的 spatial checkpoint 初始化和冻结策略，方便和前一轮实验公平对比。
- 三组 seed 结果显示，`fusion_v3` 平均 AUC 为 0.8882，略高于 `fusion_v2` 的 0.8865；但平均 Recall 为 0.7982，低于 `fusion_v2` 的 0.8226，平均 F1 也低于 `fusion_v2`。
- 因此论文中可以写“在 FFT 高频融合基础上进一步参考 DCT 频带建模思想进行优化，并取得略高的 AUC”，但不能写成全面优于 `fusion_v2`。
- 当前更稳妥的结论是：`fusion_v2` 作为系统主模型，`fusion_v3` 作为 DCT 频带建模消融实验；后续需要引入动态频带、block-DCT、attention/Q-K-V 融合或更强 backbone，进一步解决 fake 召回不稳定问题。

## 8. 是否还需要继续找论文

目前这 3 篇论文已经足够支撑课程项目的核心叙述：

1. 综述论文支撑研究背景、方法分类、数据集和评价指标。
2. 频域-空域多特征融合论文支撑 DCT 频带、空域 backbone、跨域融合和 Grad-CAM。
3. 局部相似度异常论文支撑高频噪声、局部伪造痕迹和泛化性问题。

如果继续找论文，建议不要泛泛找“deepfake detection”综述，而是围绕下面 4 个缺口定向补充：

| 缺口 | 建议检索方向 | 用途 |
|---|---|---|
| JPEG/平台压缩鲁棒性 | compressed deepfake detection, JPEG robust face forgery detection | 支撑后续鲁棒性测试，贴近微信/短视频传播场景 |
| DCT/block-DCT 频域特征 | DCT deepfake detection, block DCT face forgery | 支撑把固定 DCT 三频带升级为 block-DCT 或动态频带 |
| attention/Q-K-V 融合 | frequency spatial attention deepfake detection, cross-attention forgery detection | 支撑从 gated fusion 升级到更强融合模块 |
| 跨伪造类型泛化 | cross-manipulation deepfake detection, generalized face forgery detection | 支撑扩展 FaceSwap、Face2Face、NeuralTextures 的必要性 |

当前已完成一个“小而完整”的实验：JPEG 压缩鲁棒性测试。它不需要重新训练，而是对 test 集生成不同 quality 的 JPEG 版本并重新评估已部署的 baseline 和 fusion_v2，形成了可写入论文的实验表，直接回应真实诈骗图片会被转发压缩的问题。完整记录见 `docs/jpeg_robustness_results.md`。

## 9. 新增泛化性与鲁棒性文献记录

本轮新增 5 篇论文，整体更偏“跨数据集泛化”和“真实传播鲁棒性”。这些论文不会推翻当前的频域-空域融合路线，反而说明我们后续应该把实验重点从单纯调参转到压缩鲁棒性、跨伪造类型泛化和可解释性分析。

| 论文 | 核心思想 | 对 FaceShield 的价值 | 是否建议当前复现 |
|---|---|---|---|
| `Cross-Dataset Deepfake Detection.pdf` | 在 FaceForensics++ 上做跨伪造类型检测，并用 Grad-CAM 分析检测器为什么泛化失败 | 支撑“只在 Deepfakes 上训练不够”，也支撑系统后续加入 Grad-CAM 可解释性 | 不完整复现；可作为跨伪造类型测试和 Grad-CAM 分析依据 |
| `TOWARDS GENERALIZABLE AND ROBUST FACE MANIPULATION DETECTION.pdf` | bag-of-local-feature + Transformer，通过局部 patch 和 self-attention 学习局部伪造特征 | 支撑“伪造痕迹是局部的”，解释为什么全局 FFT 表达不足 | 不完整复现；可借鉴 patch/local feature 思路 |
| `Pay Less Attention to Deceptive Artifacts.pdf` | 关注 Online Social Networks 压缩带来的 block effect，提出 PLADA 处理压缩伪影干扰 | 强力支撑 JPEG/平台压缩鲁棒性测试，贴近 AI 换脸诈骗图片传播场景 | 不复现 PLADA；优先做 JPEG quality 扰动评估 |
| `Leveraging Real Talking Faces via Self-Supervision for Robust Forgery Detection` | 利用真实说话人视频进行自监督学习，提升伪造检测鲁棒性 | 适合作为视频级扩展依据，说明后续可以从图片级扩展到视频级/音视频一致性 | 当前不复现；属于系统后续视频级方向 |
| `Dual Contrastive Learning for General Face Forgery Detection` | 用对比学习提升一般化人脸伪造检测能力，关注跨域特征判别 | 可启发后续加入 supervised contrastive loss 或 pair-based feature learning | 当前不优先；可作为中期优化方向 |

### 9.1 对当前实验结果的解释补强

新增文献可以解释我们已有的几个现象：

1. `fusion_fft` 使用完整 FFT 幅度谱效果差，和“伪造痕迹往往是局部 patch 级别”的结论一致。全局频谱容易把局部异常稀释掉。
2. `fusion_v2` 的高频 FFT + gated fusion 比简单 concat 更合理，因为文献普遍认为模型不能只依赖单一、固定、局部 artifact。
3. `fusion_v3` 的 DCT 三频带 AUC 略高，说明频域频带建模有价值；但 Recall 不稳定，说明固定频带还不够，需要动态频带、局部 block-DCT 或 attention 融合。
4. 当前只使用 `original + Deepfakes`，不能证明系统能泛化到 FaceSwap、Face2Face、NeuralTextures 或 diffusion-based fake，这一点可以在论文里作为实验局限。
5. AI 换脸诈骗图片通常经过微信、短视频平台或截图压缩，压缩产生的 block effect 可能遮挡或伪装伪造痕迹，因此必须补鲁棒性测试。

### 9.2 可以写进论文的位置

| 论文位置 | 可写内容 |
|---|---|
| 研究背景 | deepfake 检测不仅要在同数据集上准确，还要面对跨伪造方法、跨数据集和压缩传播场景 |
| 相关工作 | 增加“泛化性与鲁棒性检测方法”小节，介绍 cross-dataset、local patch、contrastive learning 和 compression robustness |
| 算法设计依据 | 说明本项目先采用轻量化频域-空域融合模型，后续可结合 patch attention、DCT/block-DCT 和 contrastive learning |
| 实验分析 | 明确当前实验是 in-dataset image-level 检测，不能夸大为跨数据集泛化能力 |
| 总结与展望 | 写入 JPEG 压缩鲁棒性、跨伪造类型测试、Grad-CAM 可解释性、视频级检测和对比学习优化 |

### 9.3 后续最值得做的实验

优先级从高到低：

1. JPEG 压缩增强训练：已完成纯评估，下一步可在训练时随机加入 JPEG quality 扰动，观察 q30 下 Recall 是否恢复。
2. Grad-CAM 可解释性对比：对 baseline、fusion_v2、fusion_v3 各选若干 TP/FP/FN 样本，观察模型关注区域。这个实验能呼应 `Cross-Dataset Deepfake Detection`，也能服务系统热力图功能。
3. 跨伪造类型小样本测试：如果下载时间允许，补少量 FaceSwap 或 Face2Face，只做 test，不一定重新训练，用来说明当前模型的泛化局限。
4. 局部 patch 方向轻量尝试：不直接上完整 Transformer，可以先做 multi-crop/patch voting 或局部 block-DCT 特征，作为 bag-of-local-feature 的简化版本。
5. 对比学习方向暂缓：Dual Contrastive Learning 有价值，但需要重构训练目标和 batch 采样策略，当前周期内不如 JPEG 增强训练或 Grad-CAM 展示划算。

### 9.4 结论口径

推荐写法：

> 近期研究表明，深度伪造检测模型容易学习到特定伪造算法产生的局部 artifact，导致跨数据集和跨伪造类型泛化能力不足；同时，社交平台压缩产生的 block effect 可能干扰模型对真实伪造痕迹的判断。基于此，本文在完成图片级频域-空域融合检测模型的基础上，将压缩鲁棒性、局部伪造特征建模和跨伪造类型泛化作为后续优化方向。

不建议写法：

- 不建议写“本项目已解决跨数据集泛化问题”，因为目前还没有跨数据集或跨伪造类型测试。
- 不建议写“已复现 PLADA、RealForensics 或 Dual Contrastive Learning”，当前只是参考其思想。
- 不建议把视频级/音视频自监督方法写成当前系统已实现能力，当前仍是图片级检测。
