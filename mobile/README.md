# FaceShield Mobile

此目录包含 FaceShield 的 Android 原生客户端，独立于 Vue Web 前端。

## 功能范围

- Kotlin Android 应用骨架（`android-app/`）
- Jetpack Compose 页面：登录、权限引导、首页、检测记录、设置、结果详情
- 前台悬浮窗服务，提供浮动扫描按钮
- 基于 MediaProjection 的一次性屏幕截图（需用户显式授权）
- Retrofit/OkHttp 对接现有 FastAPI 后端
- DataStore 持久化 Token 和后端 URL

## 演示流程

1. 在开发机上启动后端（`python run.py` 或 Docker）
2. 手机安装 APK，确保与开发机在同一 Wi-Fi
3. 打开应用，输入后端 URL（开发机局域网 IP）和演示账号
4. 登录成功后授权悬浮窗权限和屏幕截图权限
5. 切换到目标画面，点击悬浮按钮进行截图检测
6. 查看检测结果（风险等级 + 热力图）
7. 在记录页浏览历史检测记录
8. 在设置页退出登录或更换后端地址

## 连接后端

**模拟器**默认后端 URL：

```text
http://10.0.2.2:8000/
```

**真机**需要后端在局域网可访问。确保手机和开发机在同一 Wi-Fi 下，使用开发机的局域网 IP：

```text
http://<your-computer-lan-ip>:8000/
```

Windows 上如手机无法访问，需在防火墙中放行对应端口。

## Docker 本地部署后端

从仓库根目录一键启动：

```bash
docker compose up -d --build
```

或使用 PowerShell 脚本（自动检测局域网 IP）：

```powershell
.\scripts\docker-local.ps1 up
```

脚本会输出手机端需要填写的后端 URL。详见 [docs/docker-local-deployment.md](../docs/docker-local-deployment.md)。

## 项目结构

```
mobile/
├── README.md
├── docs/          # 移动端文档
├── test-plan/     # 测试计划
└── android-app/   # Android 应用源码
    ├── app/
    │   ├── build.gradle.kts
    │   └── src/main/java/com/faceshield/mobile/
    │       ├── auth/          # 登录状态、Token 存储、用户会话
    │       ├── capture/       # MediaProjection 截图引擎
    │       ├── detection/     # 截图→上传→检测 编排
    │       ├── model/         # 数据模型 / DTO
    │       ├── network/       # Retrofit API 客户端
    │       ├── overlay/       # 悬浮窗渲染与交互
    │       ├── service/       # 前台服务（浮动保护工作流）
    │       └── ui/            # Compose 页面与导航
    └── gradle/                # Gradle wrapper
```

详见 [android-app/README.md](android-app/README.md) 和 [android-app 模块说明](android-app/app/src/main/java/com/faceshield/mobile/README.md)。
