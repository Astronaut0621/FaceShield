# 后端与模型联调说明

本文档记录 FaceShield 后端与算法模型的当前连接方式、运行配置、验证方法和已知限制。

## 1. 当前集成状态

后端算法入口为：

```python
predict_image(image_path: str) -> dict
```

业务层只调用该稳定入口，不直接依赖具体模型实现。算法后端通过环境变量切换：

| 后端 | 环境变量值 | 用途 |
|---|---|---|
| mock | `FACESHIELD_ALGORITHM_BACKEND=mock` | 前端联调、接口演示、无模型环境开发 |
| paddle | `FACESHIELD_ALGORITHM_BACKEND=paddle` | 加载 `fusion_v2` 权重执行真实推理 |

当前真实模型：

```text
model_name: FaceShield-FusionV2
model_version: fusion_v2-202607
checkpoint: model/deploy/fusion_v2/best.pdparams
config: model/deploy/fusion_v2/config.json
```

## 2. 依赖环境

后端依赖安装：

```bash
cd backend
pip install -r requirements.txt
```

当前已验证的关键版本：

```text
Python 3.13.4
paddlepaddle 3.3.1
opencv-python 4.13.0.92
numpy 2.5.1
Pillow 12.2.0
```

说明：

- 当前安装的是 CPU 版 PaddlePaddle，可以完成推理，但速度慢于 GPU 环境。
- OpenCV 需使用 4.x。曾测试 `opencv-python 5.0.0.93`，该包缺少 `CascadeClassifier`，不能用于 Haar Cascade 人脸检测。
- Paddle 首次导入可能写用户缓存目录；后端 Paddle 引擎会将缓存目录重定向到 `backend/storage/paddle_home`。

## 3. 启动真实模型后端

PowerShell：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果需要显式指定模型文件：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
$env:FACESHIELD_MODEL_PATH='D:\BigCreate\FaceShield\model\deploy\fusion_v2\best.pdparams'
$env:FACESHIELD_MODEL_CONFIG_PATH='D:\BigCreate\FaceShield\model\deploy\fusion_v2\config.json'
```

默认情况下，后端会自动使用仓库内的 `model/deploy/fusion_v2`。

## 4. 状态检查

健康检查：

```text
GET /api/health
```

返回示例：

```json
{
  "code": 200,
  "message": "FaceShield backend is running.",
  "data": {
    "status": "ok",
    "algorithm": {
      "backend": "paddle",
      "ready": true,
      "model_name": "FaceShield-FusionV2",
      "model_version": "fusion_v2-202607",
      "model_path_exists": true,
      "model_config_exists": true,
      "paddle_available": true,
      "opencv_available": true,
      "warnings": []
    }
  }
}
```

命令行检查：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
cd backend
python -c "from app.algorithm.status import get_algorithm_status; print(get_algorithm_status())"
```

如果 `ready` 为 `false`，优先检查：

1. PaddlePaddle 是否安装。
2. 模型权重路径是否存在。
3. 模型配置路径是否存在。
4. 当前 Python 环境是否与安装依赖一致。

## 5. 推理流程

真实检测接口的处理链路：

```text
上传图片
-> 校验扩展名、大小和图片内容
-> 保存原始图片
-> OpenCV Haar Cascade 检测最大人脸
-> 人脸框扩大并裁剪为正方形
-> resize 到 224x224
-> 构造 RGB 输入和高频 FFT 输入
-> Paddle fusion_v2 推理
-> 输出模型二分类结果、伪造概率、confidence
-> 计算风险等级
-> 生成可疑区域热力图
-> 保存检测记录
-> 返回前端字段
```

人脸检测失败时不会中断检测，而是回退中心裁剪，并返回：

```json
"face_detected": false
```

## 6. 前端字段契约

前端检测结果页和历史详情页主要消费：

| 字段 | 含义 |
|---|---|
| `task_id` | 检测任务编号 |
| `file_id` | 上传文件编号 |
| `label` | 模型二分类结果，`real` 或 `fake` |
| `fake_probability` | 伪造概率，范围 0 到 1 |
| `confidence` | 当前预测类别概率 |
| `risk_level` | 业务风险等级，`low`、`medium`、`high` |
| `frequency_score` | 频域分数 |
| `spatial_score` | 空域分数 |
| `original_image_url` | 原始上传图访问路径 |
| `face_crop_url` | 人脸裁剪图访问路径 |
| `face_detected` | 是否检测到人脸 |
| `heatmap_url` | 热力图访问路径 |
| `model_name` | 模型名称 |
| `model_version` | 模型版本 |
| `created_at` | 检测时间 |

静态资源通过后端 `/storage/...` 暴露，前端使用 `VITE_STORAGE_BASE_URL` 拼接完整 URL。

约定：`label` 保持 real/fake 二分类语义，默认由 `fake_probability >= 0.50`
得到；`risk_level` 由业务层根据 `fake_probability` 派生，用于前端主展示和历史筛选，不作为新的模型标签。

## 7. 模型版本管理

后端启动时会初始化两类模型版本：

```text
FaceShield-MockNet / v0.1
FaceShield-FusionV2 / fusion_v2-202607
```

active 模型由当前算法后端决定：

- `FACESHIELD_ALGORITHM_BACKEND=mock`：active 为 `FaceShield-MockNet / v0.1`
- `FACESHIELD_ALGORITHM_BACKEND=paddle`：active 为 `FaceShield-FusionV2 / fusion_v2-202607`

查询接口：

```text
GET /api/model-version
```

## 8. 已知限制

1. 当前热力图是降级可视化实现，不是严格 Grad-CAM。
2. CPU 推理可以运行，但不适合高并发或大批量检测。
3. 训练时使用 PaddlePaddle 2.4.0，当前本机推理验证使用 PaddlePaddle 3.3.1；现有权重可加载，但后续如升级模型结构，应重新做兼容性验证。
4. 当前只支持图片级检测，不支持视频级时序判断。
5. OpenCV 人脸检测失败时会中心裁剪，因此 `face_detected=false` 的结果需要谨慎解释。

## 9. 常见问题

### Paddle 导入时提示无权限写 `.cache/paddle`

后端 Paddle 引擎已自动重定向缓存。如果单独在命令行 import Paddle，可先设置：

```powershell
$env:HOME='D:\BigCreate\FaceShield\backend\storage\paddle_home'
$env:USERPROFILE='D:\BigCreate\FaceShield\backend\storage\paddle_home'
$env:PADDLE_HOME='D:\BigCreate\FaceShield\backend\storage\paddle_home'
```

### OpenCV 已安装但无法做人脸检测

确认版本为 4.x：

```bash
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'CascadeClassifier'))"
```

如果输出不支持 `CascadeClassifier`，重新安装：

```bash
python -m pip install "opencv-python<5" --force-reinstall
```

### 模型后端显示 ready=false

检查：

```bash
python -c "import paddle; print(paddle.__version__)"
```

以及：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
cd backend
python -c "from app.algorithm.status import get_algorithm_status; print(get_algorithm_status())"
```
