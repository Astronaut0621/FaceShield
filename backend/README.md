# FaceShield Backend

FaceShield 后端基于 FastAPI 构建，负责登录认证、图片上传、算法推理、结果入库、历史记录查询和静态文件访问。当前后端已经支持 `mock` 与 `paddle` 两种算法后端，默认仍使用 `mock`，便于无模型环境启动；设置环境变量后可加载 `model/deploy/fusion_v2` 中的 PaddlePaddle 权重。

## 启动

项目根目录提供 `.env.example`，可复制为 `.env` 后切换 `mock` 或 `paddle` 算法后端。

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

健康检查：

```text
GET http://localhost:8000/api/health
```

健康检查会返回：

- 服务状态
- 当前算法后端
- 模型名称和版本
- 模型权重和配置文件是否存在
- PaddlePaddle 是否可用
- OpenCV 是否可用
- 当前算法后端是否 ready

## 数据库

默认使用本地 SQLite：

```text
backend/faceshield.db
```

连接 MySQL 时设置：

```text
DATABASE_URL=mysql+pymysql://faceshield_user:your_password@localhost:3306/faceshield_db?charset=utf8mb4
```

MySQL 初始化 SQL 位于：

```text
database/sql/001_init_mysql.sql
```

## 算法后端

### mock 后端

默认值：

```text
FACESHIELD_ALGORITHM_BACKEND=mock
```

mock 后端不加载模型，使用稳定伪随机结果，适合前端联调、接口演示和无深度学习环境的开发。

### Paddle 后端

真实模型推理使用：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
```

默认模型文件：

```text
../model/deploy/fusion_v2/best.pdparams
../model/deploy/fusion_v2/config.json
```

可通过环境变量覆盖：

```text
FACESHIELD_MODEL_PATH=../model/deploy/fusion_v2/best.pdparams
FACESHIELD_MODEL_CONFIG_PATH=../model/deploy/fusion_v2/config.json
```

当前已验证 CPU 版 `paddlepaddle 3.3.1` 可加载 `fusion_v2` 权重并完成单图推理。Paddle 首次 import 可能写用户缓存目录，后端在 Paddle 引擎中将缓存重定向到：

```text
backend/storage/paddle_home
```

## 检测流程

```text
校验登录状态
-> 校验上传文件扩展名、大小和图片内容
-> 保存原始图片
-> OpenCV Haar Cascade 人脸检测
-> 检测失败时中心裁剪兜底
-> resize 到 224x224
-> 调用 mock 或 Paddle 检测引擎
-> 计算风险等级
-> 生成可疑区域热力图
-> 写入检测任务和检测结果
-> 返回前端展示字段
```

说明：Paddle 后端会基于 RGB 空域分支最后一层特征图生成 Grad-CAM 热力图；mock 模式或 Grad-CAM 生成失败时，会自动使用 fallback 热力图保证展示链路不断。

## 主要接口

- `GET /api/health`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/detect`
- `GET /api/records`
- `GET /api/records/{id}`
- `GET /api/model-version`

兼容早期前端实验的接口仍保留：

- `POST /api/files/upload`
- `POST /api/detection/start`
- `POST /api/detection/upload-and-detect`
- `GET /api/history/list`
- `GET /api/history/{task_id}`

除 `/api/health` 和 `/api/auth/login` 外，业务接口需要：

```text
Authorization: Bearer <access_token>
```

演示账号：

```text
username: demo
password: demo123456
```

## 检测结果字段

检测接口和历史详情会返回前端需要的核心字段：

```json
{
  "task_id": 1,
  "file_id": 1,
  "label": "fake",
  "fake_probability": 0.86,
  "confidence": 0.92,
  "risk_level": "high",
  "frequency_score": 0.82,
  "spatial_score": 0.88,
  "original_image_url": "/storage/uploads/example.jpg",
  "face_crop_url": "/storage/crops/example.jpg",
  "face_detected": true,
  "heatmap_url": "/storage/heatmaps/example.png",
  "model_name": "FaceShield-FusionV2",
  "model_version": "fusion_v2-202607",
  "created_at": "2026-07-06 16:00:00"
}
```

风险等级规则：

- `< 0.35`：`low`
- `0.35 - 0.80`：`medium`
- `>= 0.80`：`high`

说明：`label` 保留模型二分类结果，仍按 `fake_probability >= 0.50`
映射为 `fake`，否则为 `real`；`risk_level` 是业务展示字段，由
`fake_probability` 派生，不作为新的训练标签。

## 后端分层

```text
api/           HTTP 路由和依赖注入
services/      业务用例编排
repositories/  SQLAlchemy 数据访问
domain/        枚举、策略和应用异常
serializers/   ORM 到响应字典的转换
models/        SQLAlchemy 表模型
schemas/       Pydantic 请求/响应模型
algorithm/     算法适配层、推理引擎和预处理/后处理
core/          应用工厂、配置、数据库、日志、异常处理
utils/         通用工具
```

约定：路由层不直接查询数据库，服务层不构造 HTTP 响应，仓储层不依赖 FastAPI。

## 常用验证命令

```bash
python -m compileall app
python -c "from app.main import app; print(app.title); print(len(app.routes))"
```

查看 Paddle 后端状态：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
python -c "from app.algorithm.status import get_algorithm_status; print(get_algorithm_status())"
```
