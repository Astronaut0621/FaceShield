# FaceShield 桌面悬浮检测助手

该目录提供一个 Windows 桌面版悬浮检测助手 MVP。它不接入腾讯会议内部插件接口，而是通过用户框选屏幕区域，对会议/视频通话画面进行周期性截帧，并调用现有 FaceShield 后端完成检测。

## 功能

- 常驻置顶小窗
- 登录现有 FaceShield 后端
- 框选屏幕上的视频区域
- 按固定间隔截帧检测
- 显示最近一次实际送检的截帧预览
- 显示风险等级、伪造概率、最近检测时间
- 连续多次高风险时显示“连续预警”

## 运行前提

1. 后端已启动，例如：

   ```powershell
   cd D:\FaceShield\backend
   ..\.venv\Scripts\python.exe run.py
   ```

2. 安装桌面助手依赖：

   ```powershell
   cd D:\FaceShield
   .\.venv\Scripts\python.exe -m pip install -r desktop_assistant\requirements.txt
   ```

3. 运行悬浮助手：

   ```powershell
   .\.venv\Scripts\python.exe desktop_assistant\floating_assistant.py
   ```

   或使用启动脚本：

   ```powershell
   .\desktop_assistant\run.ps1
   ```

## 使用流程

1. 打开腾讯会议、视频通话或网页视频。
2. 启动 FaceShield 后端。
3. 启动 `floating_assistant.py`。
4. 填写后端 API，默认是 `http://127.0.0.1:8000/api`。
5. 使用演示账号登录：`demo / demo123456`。
6. 点击“框选区域”，拖拽选择对方视频画面。
7. 点击“开始检测”。
8. 悬浮窗会按检测间隔截帧，显示最近送检截图、风险等级和伪造概率。

## 技术说明

```text
视频会议画面
  -> 屏幕区域截帧
  -> POST /api/detection/upload-and-detect
  -> 后端人脸裁剪 + 模型推理 + 记录留存
  -> 悬浮窗展示风险等级
```

桌面助手本身不直接加载 Paddle 模型，避免前端/桌面端重复维护模型推理逻辑。模型推理、人脸裁剪、热力图和历史记录仍统一由后端负责。

## 烟测

无需启动真实后端也可以验证 API 客户端链路：

```powershell
cd D:\FaceShield
.\.venv\Scripts\python.exe desktop_assistant\smoke_test.py
```

通过时输出：

```text
desktop-assistant-smoke-ok
```

设计说明见 [桌面悬浮检测助手设计](../docs/floating_assistant_design.md)。

## 当前限制

- 当前是图片级模型的连续截帧检测，不是视频时序模型。
- 屏幕截帧依赖 Windows 桌面权限，部分全屏/受保护窗口可能无法截取。
- 检测间隔建议设置为 2 秒以上，避免会议时频繁请求后端。
- 如果单帧误报较多，可观察“连续预警”，不要只看一次检测结果。

## 后续增强

- 增加区域边框常驻显示
- 增加热力图弹窗
- 增加本地检测历史列表
- 增加系统托盘图标
- 增加自动窗口识别和视频区域跟踪
