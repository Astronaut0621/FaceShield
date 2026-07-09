# FaceShield

FaceShield 是一个面向 AI 换脸诈骗场景的图片级伪造人脸检测系统。用户登录后上传 JPG/PNG 图片，后端完成人脸裁剪、模型推理、伪造概率计算、风险等级映射、可疑区域热力图生成、检测记录保存和历史记录查询。

提供四种客户端：
- **Web 前端**：Vue 3 + Vite，适合桌面浏览器使用
- **桌面悬浮助手**：Windows 置顶小窗，支持框选视频会议区域并周期性截帧检测
- **Android 移动端**：Kotlin + Jetpack Compose，支持屏幕截图实时检测
- **Docker 本地部署**：一键启动后端，手机通过局域网连接

## 当前状态

- 后端：FastAPI + SQLAlchemy，支持 SQLite 开发库和 MySQL 兼容 SQL。
- 前端：Vue 3 + Vite，包含登录、检测工作台、结果页、历史记录和详情页。
- 桌面悬浮助手：Python + Tkinter，支持登录、框选屏幕区域、周期性截帧、风险提示。
- 移动端：Kotlin + Jetpack Compose Android 原生应用，支持登录、悬浮窗截图检测、检测记录查看、退出登录。
- 算法：已接入 `mock` 与 `paddle` 两种检测后端。
- 模型：默认部署模型为 `FaceShield-FusionV2 / fusion_v2-202607`，权重位于 `model/deploy/fusion_v2`。
- 部署：支持 Docker Compose 一键启动，mock 模式无需 GPU，Paddle 模式可挂载模型权重进行真实推理。
- 预处理：上传图片会保存原图，随后进行人脸检测裁剪；OpenCV 可用时使用 Haar Cascade，失败时回退中心裁剪。
- 热力图：当前后端生成可展示的降级热力图，用于打通前端展示链路；严格 Grad-CAM 仍属于后续增强项。

## 目录结构

```text
backend/     FastAPI 服务、认证、上传、检测、历史记录、算法适配层
frontend/    Vue 3 + Vite 前端页面与业务服务
desktop_assistant/  Windows 桌面悬浮检测助手
mobile/      Android 原生应用（Kotlin + Jetpack Compose）
training/    PaddlePaddle 训练、评估、单图预测脚本
model/       部署权重、模型配置与指标文件
database/    MySQL 建表 SQL、schema 和数据库说明
docs/        算法设计、实验结果、开发说明和 Docker 部署文档
tools/       FaceForensics++ 下载、抽帧、人脸裁剪辅助脚本
scripts/     部署辅助脚本（docker-local.ps1）
```

## 后端启动

首次本地运行可以先复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

`.env` 中默认使用 `mock` 算法后端，适合前端联调和无 Paddle 环境演示：

```env
FACESHIELD_ALGORITHM_BACKEND=mock
```

如果要使用真实 Paddle 模型和在线 Grad-CAM 热力图，将 `.env` 改为：

```env
FACESHIELD_ALGORITHM_BACKEND=paddle
FACESHIELD_MODEL_PATH=D:/FaceShield/model/deploy/fusion_v2/best.pdparams
FACESHIELD_MODEL_CONFIG_PATH=D:/FaceShield/model/deploy/fusion_v2/config.json
```

启动后端（二选一）：

```bash
# 方式一：使用 run.py（推荐，开发用）
cd backend
python run.py

# 方式二：直接使用 uvicorn
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

默认使用 SQLite：`backend/faceshield.db`。如需连接 MySQL，设置 `DATABASE_URL`：

```text
DATABASE_URL=mysql+pymysql://faceshield_user:your_password@localhost:3306/faceshield_db?charset=utf8mb4
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

## 桌面悬浮助手（Windows）

桌面悬浮助手面向腾讯会议、视频通话和网页视频等电脑端场景。它不会接入会议软件内部插件接口，而是让用户框选屏幕上的视频区域，周期性截帧后调用后端检测。

安装依赖：

```powershell
cd D:\FaceShield
.\.venv\Scripts\python.exe -m pip install -r desktop_assistant\requirements.txt
```

运行：

```powershell
.\.venv\Scripts\python.exe desktop_assistant\floating_assistant.py
```

也可以使用启动脚本：

```powershell
.\desktop_assistant\run.ps1
```

使用流程：

1. 启动后端。
2. 打开腾讯会议或其他视频通话窗口。
3. 打开桌面悬浮助手并登录。
4. 点击“框选区域”，选择对方视频画面。
5. 点击“开始检测”，悬浮窗会显示风险等级和伪造概率。

详细说明见 [桌面悬浮检测助手](desktop_assistant/README.md)。

## 移动端（Android）

Android 原生应用，通过悬浮窗截图并提交后端进行 AI 换脸检测。

### 构建

用 Android Studio 打开 `mobile/android-app/` 目录，等待 Gradle 同步后构建即可。

命令行构建：

```bash
cd mobile/android-app
./gradlew :app:assembleDebug
```

### 连接后端

**模拟器**使用：

```text
http://10.0.2.2:8000/
```

**真机**需要后端在局域网可访问。确保手机和开发机在同一 Wi-Fi 下，使用开发机的局域网 IP：

```text
http://<your-computer-lan-ip>:8000/
```

### 演示流程

1. 启动后端（直接 `python run.py` 或 Docker）
2. 手机安装 APK，打开应用
3. 输入后端 URL，输入演示账号登录
4. 点击悬浮按钮授权屏幕截图
5. 切换到目标画面（如聊天界面的人脸照片），点击悬浮按钮截图检测
6. 查看检测结果（风险等级 + 热力图）
7. 在"记录"页查看历史检测记录
8. 在"设置"页退出登录或更换后端地址

详细说明见 [mobile/android-app/README.md](mobile/android-app/README.md)。

## Docker 本地部署

适合快速启动后端供真机演示，无需手动配置 Python 环境。

### Mock 模式（推荐，无需 GPU）

```powershell
cd D:\BigCreate\FaceShield
.\scripts\docker-local.ps1 up
```

脚本会输出手机端需要填写的后端 URL，如 `http://192.168.128.204:8000/`。

### Paddle 模式（需要模型权重）

```powershell
.\scripts\docker-local.ps1 up -Paddle
```

### 其他操作

```powershell
.\scripts\docker-local.ps1 status     # 查看状态
.\scripts\docker-local.ps1 logs       # 查看日志
.\scripts\docker-local.ps1 test       # 验证后端是否正常
.\scripts\docker-local.ps1 down       # 停止容器
.\scripts\docker-local.ps1 up -Port 8010   # 使用其他端口
```

详细说明见 [docs/docker-local-deployment.md](docs/docker-local-deployment.md)。

## 演示账号

后端启动时会自动创建演示账号：

```text
username: demo
password: demo123456
```

可通过环境变量 `DEMO_USERNAME`、`DEMO_PASSWORD`、`DEMO_DISPLAY_NAME` 自定义。

## 主要接口

公开接口：

- `GET /api/health` — 健康检查
- `POST /api/auth/login` — 登录
- `GET /api/mobile/bootstrap` — 移动端启动前探活

需认证的接口（请求头带 `Authorization: Bearer <access_token>`）：

- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/detect` — 上传图片并检测
- `GET /api/records` — 检测记录列表
- `GET /api/records/{id}` — 检测记录详情
- `GET /api/model-version` — 模型版本信息

API 交互式文档：

```text
http://localhost:8000/docs
```

## 推荐阅读

- [后端说明](backend/README.md)
- [前端说明](frontend/README.md)
- [移动端说明](mobile/README.md)
- [Android 应用说明](mobile/android-app/README.md)
- [Docker 本地部署](docs/docker-local-deployment.md)
- [模型产物说明](model/README.md)
- [后端与模型联调说明](docs/backend_model_integration.md)
- [算法设计](docs/algorithm_design.md)
- [实验结果](docs/experiment_results.md)
