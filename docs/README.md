# FaceShield 文档索引

本目录存放项目设计、算法实验、后端模型联调和论文/答辩材料辅助文档。

## 推荐阅读顺序

1. [开发说明书](development_spec.md)：系统目标、模块划分、接口和交付物。
2. [算法设计](algorithm_design.md)：图片级伪造人脸检测任务、数据处理、模型路线和评估指标。
3. [实验结果](experiment_results.md)：baseline、fusion_fft、fusion_v2 的指标对比和结论。
4. [后端与模型联调说明](backend_model_integration.md)：后端加载 Paddle 模型、环境变量、健康检查和故障排查。
5. [训练论文材料整理](training_paper_notes.md)：论文或答辩中可复用的算法描述和实验表述。
6. [Word 模板插入映射](word_template_training_insert_map.md)：课程文档写作时的内容映射建议。
7. [跨域泛化实验方案](cross_domain_evaluation.md)：FaceForensics++ 跨伪造类型和 Celeb-DF v2 跨数据集评估流程。

## 当前实现边界

- 系统主流程是图片级检测，不做视频级时序判断。
- 后端支持 `mock` 和 `paddle` 两种算法后端。
- `paddle` 后端已能加载 `model/deploy/fusion_v2` 权重进行真实推理。
- 人脸裁剪优先使用 OpenCV Haar Cascade，失败时中心裁剪兜底。
- Paddle 后端已接入 Grad-CAM 热力图；mock 模式或生成失败时使用 fallback 热力图。
- 历史记录按登录用户隔离。
