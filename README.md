# FaceShield

FaceShield 是一个面向 AI 换脸诈骗场景的图片级伪造人脸检测系统。用户登录后上传 JPG/PNG 图片，后端完成人脸裁剪、模型推理、伪造概率计算、风险等级映射、可疑区域热力图生成、检测记录保存和历史记录查询。

## 当前状态

- 后端：FastAPI + SQLAlchemy，支持 SQLite 开发库和 MySQL 兼容 SQL。
- 前端：Vue 3 + Vite，包含登录、检测工作台、结果页、历史记录和详情页。
- 算法：已接入 `mock` 与 `paddle` 两种检测后端。
- 模型：默认部署模型为 `FaceShield-FusionV2 / fusion_v2-202607`，权重位于 `model/deploy/fusion_v2`。
- 预处理：上传图片会保存原图，随后进行人脸检测裁剪；OpenCV 可用时使用 Haar Cascade，失败时回退中心裁剪。
- 热力图：当前后端生成可展示的降级热力图，用于打通前端展示链路；严格 Grad-CAM 仍属于后续增强项。

## 目录结构

```text
backend/    FastAPI 服务、认证、上传、检测、历史记录、算法适配层
frontend/   Vue 3 + Vite 前端页面与业务服务
training/   PaddlePaddle 训练、评估、单图预测脚本
model/      部署权重、模型配置与指标文件
database/   MySQL 建表 SQL、schema 和数据库说明
docs/       算法设计、实验结果、开发说明和联调文档
tools/      FaceForensics++ 下载、抽帧、人脸裁剪辅助脚本
```

## 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

默认使用 SQLite：`backend/faceshield.db`。如需连接 MySQL，设置 `DATABASE_URL`：

```text
DATABASE_URL=mysql+pymysql://faceshield_user:your_password@localhost:3306/faceshield_db?charset=utf8mb4
```

默认算法后端是 `mock`，适合快速演示和无模型环境：

```text
FACESHIELD_ALGORITHM_BACKEND=mock
```

使用真实 Paddle 模型：

```powershell
$env:FACESHIELD_ALGORITHM_BACKEND='paddle'
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```text
GET http://localhost:8000/api/health
```

该接口会返回当前算法后端、模型路径是否存在、Paddle/OpenCV 是否可用等状态。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认请求：

```text
http://localhost:8000/api
```

如需修改，设置 `VITE_API_BASE_URL` 和 `VITE_STORAGE_BASE_URL`。

## 演示账号

后端启动时会自动创建演示账号：

```text
username: demo
password: demo123456
```

公开接口：

- `/api/health`
- `/api/auth/login`

检测和历史记录接口需要请求头：

```text
Authorization: Bearer <access_token>
```

## 推荐阅读

- [后端说明](backend/README.md)
- [前端说明](frontend/README.md)
- [模型产物说明](model/README.md)
- [后端与模型联调说明](docs/backend_model_integration.md)
- [算法设计](docs/algorithm_design.md)
- [实验结果](docs/experiment_results.md)
