# Word 模板中训练内容的插入位置建议

依据模板文件：`docs/团队名 - 班级（工程项目开发综合实践大作业模板）.doc`

分析时间：2026-07-05

本模板是工程项目开发综合实践文档，不是单独的算法论文。因此训练内容不要集中塞到一个“论文实验”章节，而应该分散写入“概要设计、详细设计、系统测试、总结与展望”等位置。其中第六章和第七章是重点。

## 1. 最推荐写入的位置

| 优先级 | Word 模板章节 | 应写内容 | 对应素材 |
|---|---|---|---|
| 最高 | 六、系统详细设计 -> 3．设计说明 | 算法模块设计、数据预处理、baseline、fusion_fft、fusion_v2、训练流程、推理流程 | `training/dataset.py`、`training/models.py`、`training/train.py` |
| 最高 | 六、系统详细设计 -> 5. 实现结果 | 本轮训练已经实现的内容、训练输出文件、best checkpoint、模型指标摘要，重点写 fusion_v2 主配置 | `model/outputs/`、`model/summary/metrics_summary.csv`、AutoDL 输出 |
| 最高 | 七、系统测试 -> 2．测试概要 | 模型测试环境、测试集规模、评价指标、测试对象 | `model/outputs/*/config.json` |
| 最高 | 七、系统测试 -> 3．测试结果及发现 | baseline、fusion_fft、fusion_v2 的指标对比表、训练曲线图、调参发现 | `metrics_summary.csv`、`training_curves.svg`、AutoDL 输出 |
| 高 | 七、系统测试 -> 5．分析摘要 | 模型能力、缺陷限制、改进建议、是否达到当前可用目标，注意 fusion_v2 只能写“一定提升” | `experiment_summary.md`、`training_paper_notes.md` |
| 高 | 九、总结与展望 | 本轮算法完成情况、不足和后续改进方向 | `training_paper_notes.md` 第 6、8 节 |

## 2. 按 Word 目录逐章判断

### 一、引言

可少量写，不放训练细节。

适合位置：

- `1.2现状及意义`
- `1.3背景`

建议写：

- AI 换脸诈骗、Deepfake 检测的背景和意义。
- FaceShield 做的是图片级伪造人脸检测。
- 系统使用深度学习模型输出伪造概率，为用户提供辅助判断。

不建议写：

- 不放训练指标大表。
- 不展开 baseline/fusion_fft 结构。

### 二、系统可行性分析

可写训练相关的技术可行性和限制。

适合位置：

- `2.1要求`
- `2.5评价尺度`
- `4.5局限性`
- `4.6技术条件方面的可行性`

建议写：

- 输入为 224x224 人脸裁剪图，输出为 real/fake 和伪造概率。
- 评价尺度采用 Accuracy、AUC、Precision、Recall、F1。
- PaddlePaddle、FaceForensics++、GPU 训练说明技术条件可满足。
- 当前只使用 `original + Deepfakes`，且只做图片级检测，这是系统局限。

可用表述：

> 从技术条件看，本项目可利用 PaddlePaddle 深度学习框架和公开 FaceForensics++ 数据集完成伪造人脸检测模型训练。训练阶段以人脸裁剪图为输入，采用 Accuracy、AUC、Precision、Recall 和 F1 作为模型效果评价指标。当前系统主要面向图片级检测，尚未实现视频级时序建模。

### 三、系统开发计划

模板里这一章已经写了不少 FaceShield 内容，只需要补充或微调。

适合位置：

- `2.1工作内容`
- `2.3.1程序`
- `2.4验收标准`
- `2.5完成项目的最迟期限`

建议写：

- `2.1工作内容` 中可补充“完成 baseline、fusion_fft 与 fusion_v2 对比实验”。
- `2.3.1程序` 中可说明“训练代码、模型权重和实验汇总文件”是算法交付内容。
- `2.4验收标准` 中可写模型在测试集上达到可用效果，当前 fusion_v2 主配置 seed42 达到 test AUC 0.9014、F1 0.8348；三 seed 平均 test AUC 为 0.8865、F1 为 0.8082。
- `2.5完成项目的最迟期限` 中可把 7 月 6 日/7 月 7 日训练结果对应进去。

注意：

- 不要把完整实验分析写在第三章；第三章只是计划与交付。

### 四、系统需求分析

训练内容不是这一章重点，但可以支撑“系统需要什么”。

适合位置：

- `2.1.4产品功能`
- `3.1系统流程图`
- `3.2数据流图及用例模型`
- `3.3数据字典`
- `4.1运行环境`
- `4.2支持软件`

建议写：

- 产品功能：图片上传、人脸预处理、模型推理、伪造概率、风险等级、检测记录。
- 数据流图：用户图片 -> 后端上传接口 -> 人脸裁剪 -> 模型推理 -> 检测结果 -> 数据库存储。
- 数据字典：`image_path`、`model_version`、`fake_probability`、`risk_level`、`prediction`、`created_at`。
- 支持软件：Python、FastAPI、PaddlePaddle、Vue、openGauss。

不建议写：

- 不在需求分析里写“为什么 fusion_fft 不如 baseline”，这是测试分析内容。

### 五、系统概要设计

这里适合写算法模块在系统中的位置，不适合写太细的代码。

适合位置：

- `2.2运行环境`
- `2.3基本设计概念和处理流程`
- `2.4软件结构设计`
- `3.3内部接口`
- `4.1运行模块组合`

建议写：

- 算法模块位于后端推理流程中，负责对人脸图像输出 real/fake 和伪造概率。
- 系统处理流程为：图片上传 -> 人脸检测裁剪 -> 模型预处理 -> 模型推理 -> 风险等级计算 -> 结果保存与展示。
- 软件结构中可加入 `training/`、`backend/app/algorithm/`、`frontend/`、`database/` 四类模块。
- 内部接口可以写 `predict_image(image_path)`，后端业务层调用算法模块。

可用表述：

> 算法模块是系统核心处理模块之一，负责将上传图片转换为模型输入，并输出伪造概率和预测类别。系统设计上将训练代码、推理代码和后端业务接口分离，训练阶段生成模型权重文件，部署阶段由后端算法接口加载模型并完成单图推理。

### 六、系统详细设计

这是训练内容最该写的章节。

适合位置：

- `2．程序系统的结构`
- `3．设计说明`
- `5. 实现结果`

建议新增或改写的小节：

```text
3.1 算法训练模块
3.1.1 数据集读取与预处理
3.1.2 RGB baseline 模型
3.1.3 初版频域-空域融合模型 fusion_fft
3.1.4 优化后的频域-空域融合模型 fusion_v2
3.1.5 模型训练与最佳模型选择
3.1.6 单图推理流程
```

在 `3.1.1 数据集读取与预处理` 写：

- 使用 `face_manifest_clean.csv`。
- train/val/test 为 3769/1284/1092。
- real/fake 标签为 0/1。
- 输入统一 resize 到 224x224。
- 训练增强包括随机水平翻转、亮度/对比度/颜色扰动。
- fusion_fft 额外生成完整 FFT 幅度谱。
- fusion_v2 额外生成高频 FFT 输入，抑制低频中心区域。

在 `3.1.2 RGB baseline 模型` 写：

- RGB face crop -> TinyBackbone -> 全局平均池化 -> Dropout -> Linear 分类。
- 作为对比基线。

在 `3.1.3 初版频域-空域融合模型 fusion_fft` 写：

- RGB 分支学习空间纹理。
- FFT 分支学习频域伪影。
- 两个分支输出 concat 后分类。

在 `3.1.4 优化后的频域-空域融合模型 fusion_v2` 写：

- 使用 baseline checkpoint 初始化 spatial branch。
- 频域分支使用高频 FFT 输入，减少低频整体亮度和结构信息干扰。
- 采用 gating residual fusion，让模型控制频域特征注入强度。
- 当前推荐配置为 `freeze-spatial-epochs=3`、`lr=5e-4`。

在 `3.1.5 模型训练与最佳模型选择` 写：

- PaddlePaddle 2.4.0。
- AdamW，baseline/fusion_fft 使用 lr=0.001，fusion_v2 主配置使用 lr=0.0005，batch size=32，weight decay=0.0001，dropout=0.3。
- 最大 30 epoch，patience=8。
- 以验证集 AUC 保存 best checkpoint。

在 `5. 实现结果` 写：

- 训练产物路径。
- `baseline/best.pdparams`、`fusion_fft/best.pdparams` 与 `fusion_v2_seed*/best.pdparams`。
- 指标汇总文件。
- 简短说明 fusion_v2 是当前频域-空域融合主模型，baseline 是对照模型，fusion_fft 是初版探索实验。

### 七、系统测试

这是训练结果和实验结论最该写的章节。

适合位置：

- `2．测试概要`
- `3．测试结果及发现`
- `4．对软件功能的结论`
- `5．分析摘要`
- `6．测试资源消耗`

在 `2．测试概要` 写：

| 测试项 | 测试内容 |
|---|---|
| 模型训练测试 | 验证 baseline、fusion_fft 与 fusion_v2 能否完成训练并保存 checkpoint |
| 模型指标测试 | 在独立测试集上计算 Accuracy、AUC、Precision、Recall、F1 |
| 模型对比测试 | 比较 RGB baseline、初版 FFT concat 融合模型与 fusion_v2 门控融合模型的检测效果 |
| 推理流程测试 | 验证单张图片能否输出预测类别和伪造概率 |

在 `3．测试结果及发现` 放本轮核心指标表：

| 模型 | best epoch | val AUC | test Accuracy | test AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 14 | 0.8479 | 0.7811 | 0.8554 | 0.7413 | 0.8624 | 0.7973 | 0.6325 |
| fusion_fft | 15 | 0.7678 | 0.6941 | 0.7617 | 0.6881 | 0.7083 | 0.6980 | 0.9340 |
| fusion_v2 主配置 seed42 | 14 | 0.8698 | 0.8333 | 0.9014 | 0.8259 | 0.8440 | 0.8348 | 0.7719 |

也可以补充三 seed 平均表：

| 模型 | Accuracy | AUC | Precision | Recall | F1 | Loss |
|---|---:|---:|---:|---:|---:|---:|
| baseline 平均 | 0.7967 | 0.8805 | 0.7828 | 0.8257 | 0.8025 | 0.6318 |
| fusion_v2 平均 | 0.8056 | 0.8865 | 0.7956 | 0.8226 | 0.8082 | 0.7795 |

建议配图：

- `model/summary/training_curves.svg`

在 `5.1能力` 写：

- 系统已具备图片级伪造人脸检测模型训练能力。
- fusion_v2 主配置 seed42 在测试集上达到 test AUC 0.9014、F1 0.8348；三 seed 平均 test AUC 为 0.8865、F1 为 0.8082。
- 训练流程能生成配置、历史、最佳权重和测试指标。

在 `5.2缺陷和限制` 写：

- 初版 fusion_fft 未超过 baseline，但优化后的 fusion_v2 三 seed 平均指标略高于 baseline。
- fusion_v2 不同 seed 下仍有波动，不能写成“显著提升”。
- 当前只使用 FaceForensics++ 的 `original + Deepfakes`。
- 当前评估是图片级，不含视频级时序一致性检测。
- 初版 fusion_fft 使用全局 FFT 幅度谱，对局部伪造痕迹表达不足；fusion_v2 已改为高频 FFT，但稳定性仍需优化。

在 `5.3建议` 写：

- 引入 DCT/block-DCT、多尺度 FFT。
- 在当前 gating 融合基础上继续尝试 attention 或 cross-modal interaction。
- 使用 ResNet18、MobileNetV3 或 EfficientNet。
- 扩展 Face2Face、FaceSwap、NeuralTextures 等伪造类型。

在 `6．测试资源消耗` 写：

| 模型 | 训练耗时 | 设备 | 框架 |
|---|---:|---|---|
| baseline | 426.66s | GPU `gpu:0` | PaddlePaddle 2.4.0 |
| fusion_fft | 681.53s | GPU `gpu:0` | PaddlePaddle 2.4.0 |
| fusion_v2 主配置 seed42 | 713.61s | GPU `gpu:0` | PaddlePaddle 2.4.0 |

### 八、系统用户操作手册

训练内容基本不写这里。

适合写：

- 用户怎么上传图片。
- 用户怎么查看伪造概率、风险等级、检测记录。

不建议写：

- 不写模型训练细节。
- 不写实验指标表。

### 九、总结与展望

适合写本轮训练结论，但要简洁。

建议写：

> 本项目完成了图片级伪造人脸检测系统的主要功能设计与原型实现，并完成了 RGB baseline、初版 fusion_fft 和优化后 fusion_v2 的对比实验。实验结果表明，初版全局 FFT 幅度谱和简单特征拼接未能超过 baseline；进一步采用高频 FFT、baseline checkpoint 初始化和门控残差融合后，fusion_v2 在三组随机种子的平均 AUC、Accuracy 和 F1 上均略高于 baseline，可作为当前频域-空域融合主模型。由于 fusion_v2 在不同 seed 下仍存在波动，后续需要继续优化频域特征表达、融合策略和模型 backbone。

## 3. 最终落点建议

如果时间紧，优先只写这几个位置：

1. `六、系统详细设计 -> 3．设计说明`：写算法结构和训练流程。
2. `六、系统详细设计 -> 5. 实现结果`：写训练产物和模型实现结果。
3. `七、系统测试 -> 3．测试结果及发现`：放指标表和训练曲线。
4. `七、系统测试 -> 5．分析摘要`：写初版 fusion_fft 的不足、fusion_v2 的改进和仍存在的稳定性问题。
5. `九、总结与展望`：写最终结论和后续方向。

## 4. 不要这样写

- 不要把训练指标写进 `一、引言`，那里只写背景意义。
- 不要在 `三、系统开发计划` 里展开实验分析，那里只写计划、交付物和验收标准。
- 不要把初版 fusion_fft 写成“性能提升方法”，本轮实验结果不支持。
- 不要把 fusion_v2 写成“显著提升”，只能写平均指标有一定提升。
- 不要写系统已经具备视频级检测能力，当前是图片级/帧级检测。
- 不要写覆盖全部 Deepfake 类型，当前训练只覆盖 `original + Deepfakes`。
