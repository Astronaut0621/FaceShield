# FaceShield Algorithm Adapter

`backend/app/algorithm` 是后端与算法模型之间的适配层。业务服务只调用稳定入口：

```python
predict_image(image_path: str) -> dict
```

具体推理实现由 `FACESHIELD_ALGORITHM_BACKEND` 决定。

## 支持的后端

| 后端 | 名称 | 说明 |
|---|---|---|
| mock | `mock` | 稳定伪随机输出，用于前端联调和无模型环境 |
| Paddle | `paddle` | 加载 `model/deploy/fusion_v2` 的 PaddlePaddle 权重进行真实推理 |

默认值：

```text
FACESHIELD_ALGORITHM_BACKEND=mock
```

真实模型：

```text
FACESHIELD_ALGORITHM_BACKEND=paddle
```

## 处理流程

当前检测主流程由服务层编排：

```text
原始上传图
-> preprocess.crop_face_for_detection
-> predict_image
-> postprocess.generate_fallback_heatmap
-> DetectionService 保存结果
```

`crop_face_for_detection` 会优先使用 OpenCV Haar Cascade 检测最大人脸；OpenCV 不可用或检测失败时回退中心裁剪。输出统一 resize 到 `224x224`。

## 目录说明

```text
contracts/    DetectionInput、DetectionOutput 和 DetectionEngine 协议
models/       mock 与 Paddle 检测引擎、Paddle 模型结构
pipeline/     验证、预处理、特征提取、推理、后处理阶段
postprocess/  热力图生成和路径映射
preprocess.py 人脸裁剪和检测输入预处理
status.py     算法后端状态检查
config.py     模型路径、版本和后端配置
```

## Paddle 模型

Paddle 后端默认读取：

```text
model/deploy/fusion_v2/best.pdparams
model/deploy/fusion_v2/config.json
```

配置来源：

```text
FACESHIELD_MODEL_PATH
FACESHIELD_MODEL_CONFIG_PATH
FACESHIELD_MODEL_NAME
FACESHIELD_MODEL_VERSION
```

当前默认模型元数据：

```text
model_name: FaceShield-FusionV2
model_version: fusion_v2-202607
```

## 热力图说明

当前后端生成的是降级可视化热力图，用于前端展示和检测记录闭环，不是严格 Grad-CAM。后续如果接入 Grad-CAM，应保持 `heatmap_url` 字段不变，替换 `postprocess` 中的生成逻辑即可。

## 状态检查

```python
from app.algorithm.status import get_algorithm_status

print(get_algorithm_status())
```

该函数会返回当前后端、模型路径、Paddle/OpenCV 可用性和 warning 信息，并已接入 `/api/health` 与 `/api/model-version`。
