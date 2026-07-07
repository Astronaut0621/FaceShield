# FaceShield 学年论文

> **工程项目开发综合实践（2025-2026 学年第三学期）**  
> 依据模板：`FaceShield.doc`  
> 说明：请将封面信息、团队分工、截图、E-R 图、界面原型图等按 Word 模板格式排版后提交。

---

## 封面信息（请自行填写）

| 项目 | 内容 |
|------|------|
| 题　　目 | 基于频域-空域特征融合的 AI 换脸诈骗伪造人脸检测系统 FaceShield |
| 团　　队 | （填写团队名称） |
| 姓　　名 | （填写成员姓名） |
| 所在学院 | 计算机科学与技术学院 |
| 班　　级 | （填写班级） |
| 指导教师 | 买合木提·买买提 |
| 职　　称 | 高级实验师 |
| 完成日期 | 2026 年 7 月 9 日 |

---

## 目录

- [一、引言](#一引言)
- [二、系统可行性分析](#二系统可行性分析)
- [三、系统开发计划](#三系统开发计划)
- [四、系统需求分析](#四系统需求分析)
- [五、系统概要设计](#五系统概要设计)
- [六、系统详细设计](#六系统详细设计)
- [七、系统测试](#七系统测试)
- [八、系统用户操作手册](#八系统用户操作手册)
- [九、总结与展望](#九总结与展望)
- [参考文献](#参考文献)

---

# 一、引言

## 1.1 开发目的

本文档是 FaceShield 伪造人脸检测系统的工程项目开发综合实践文档，面向指导教师、答辩评审人员及项目开发团队成员。文档旨在完整记录系统从可行性分析、需求分析、概要设计、详细设计、实现测试到用户手册的全过程，为项目验收、答辩和后续改进提供依据。

## 1.2 现状及意义

随着 DeepFake、FaceSwap 等深度伪造技术的快速发展，AI 换脸诈骗已成为网络安全和社会治理领域的重要威胁。攻击者可通过伪造人脸图像或视频冒充他人身份，实施金融诈骗、虚假信息传播和身份冒用等违法行为。传统人工鉴别方式效率低、主观性强，难以应对大规模、高逼真度的伪造内容。

国内外已有 FaceForensics++、Celeb-DF、DFDC 等公开数据集及相关检测研究，但多数成果仍停留在算法实验阶段，缺少面向普通用户可操作的检测平台。因此，开发一套集“图片上传—模型推理—风险展示—历史追溯”于一体的 Web 检测系统，具有明确的现实意义：

1. 为普通用户提供伪造人脸辅助鉴别工具；
2. 为课程项目提供算法、后端、前端、数据库协同开发的完整工程实践；
3. 为后续扩展视频检测、多伪造类型识别和模型版本管理奠定基础。

## 1.3 背景

**系统名称**：FaceShield（面向 AI 换脸诈骗场景的伪造人脸检测系统）

**项目提出者**：新疆大学计算机科学与技术学院工程项目开发综合实践课程

**开发者**：FaceShield 项目开发团队（算法、后端、前端、数据库分工协作）

**用户对象**：具备基本 Web 操作能力的普通用户、演示测试人员及课程评审人员

**实现环境**：

- 前端：Vue 3 + Vite，运行于浏览器
- 后端：Python FastAPI，默认端口 8000
- 算法：PaddlePaddle 深度学习框架
- 数据库：openGauss 兼容设计，开发阶段可使用 SQLite

**系统关系**：FaceShield 为独立 Web 应用，通过 RESTful API 连接前端与后端；后端调用本地算法模块完成推理，并将检测记录持久化到数据库；静态图片与热力图通过 `/storage` 路径对外提供访问。

---

# 二、系统可行性分析

## 2 可行性研究的前提

FaceShield 项目要求在 2025-2026 学年第三学期内完成一个可演示的 MVP 系统，支持单张图片级伪造人脸检测，不要求视频级检测和公开用户注册。

## 2.1 要求

### 功能要求

1. 用户登录与退出；
2. 单张 JPG/PNG 图片上传；
3. 人脸检测与裁剪；
4. 伪造概率、风险等级、检测结论输出；
5. 频域/空域特征分数展示；
6. 可疑区域热力图展示；
7. 检测历史记录查询与详情查看；
8. 模型版本管理与模型选择。

### 性能要求

1. 单张图片检测响应时间控制在可接受范围内（开发环境通常 10 秒内）；
2. 前端页面加载与交互流畅；
3. 支持多用户历史记录隔离。

### 输入输出

| 类型 | 说明 |
|------|------|
| 输入 | 用户账号密码；JPG/JPEG/PNG 人脸图片；可选模型 ID |
| 输出 | JSON 检测结果；原图/裁剪图/热力图 URL；历史记录列表 |

### 处理流程

```text
用户登录 -> 上传图片 -> 选择模型 -> 后端保存文件
-> 人脸裁剪 -> 模型推理 -> 风险等级映射 -> 热力图生成
-> 结果入库 -> 前端展示 -> 历史查询
```

### 安全与保密

1. 密码仅保存 hash，不保存明文；
2. JWT Token 鉴权；
3. 用户只能访问本人检测记录；
4. 401 未授权请求自动跳转登录页。

## 2.2 目标

1. 建立完整的图片级 DeepFake 检测原型系统；
2. 实现频域-空域融合模型与 RGB baseline 的对比实验；
3. 形成可演示的前后端分离 Web 系统；
4. 完成检测记录持久化与可视化展示；
5. 满足课程项目答辩与文档验收要求。

## 2.3 条件、假定和限制

| 项目 | 说明 |
|------|------|
| 运行寿命 | 课程项目周期内持续可用 |
| 数据来源 | FaceForensics++ c23 中 original + Deepfakes |
| 检测粒度 | 图片级/帧级，不含视频时序建模 |
| 伪造类型 | 当前主要覆盖 Deepfakes |
| 开发环境 | Windows/Linux，Python 3.10+，Node.js 18+ |
| GPU | 模型训练需要 GPU，部署推理可选 CPU/GPU |

## 2.4 进行可行性研究的方法

采用文献调研、原型开发、对照实验和系统联调相结合的方法：

1. 调研 DeepFake 检测相关论文与公开数据集；
2. 采用敏捷迭代方式搭建 MVP；
3. 通过 baseline 与 fusion 模型对比验证算法路线；
4. 通过接口测试和功能测试验证系统可用性。

## 2.5 评价尺度

| 尺度 | 内容 |
|------|------|
| 功能完整性 | 是否覆盖登录、检测、结果展示、历史记录 |
| 算法效果 | Accuracy、AUC、F1 等指标 |
| 开发周期 | 是否按期完成 |
| 易用性 | 页面是否清晰、流程是否顺畅 |
| 可扩展性 | 是否支持模型切换与后续功能扩展 |

## 3 对现有系统的分析

### 3.1 处理流程和数据流程

现有手工鉴别流程为：用户收到可疑图片 -> 人工观察 -> 凭经验判断 -> 无法留存记录。该方式无法量化风险，也无法追溯历史。

### 3.2 工作负荷

人工鉴别依赖专业人员，普通用户难以使用，无法满足大规模筛查需求。

### 3.3 局限性

1. 无统一检测平台；
2. 无可视化概率与热力图；
3. 无历史记录；
4. 无法复现检测过程；
5. 难以支撑课程项目的工程化展示。

## 4 所建议的系统

### 4.1 对所建议系统的说明

FaceShield 采用前后端分离架构，以 FastAPI 为业务中枢，以 PaddlePaddle 模型为检测核心，以 Vue 前端为交互界面，以 openGauss/SQLite 为数据存储，实现“上传即检测、结果可解释、记录可追溯”。

### 4.2 处理流程和数据流程

```text
[用户] --登录--> [前端] --Token--> [后端 Auth]
[用户] --上传图片+模型ID--> [后端 Detection]
    -> [FileService 保存原图]
    -> [Algorithm 人脸裁剪]
    -> [Paddle/Mock 推理]
    -> [RiskPolicy 风险映射]
    -> [Heatmap 生成]
    -> [DetectionRepository 入库]
[前端] <--JSON+图片URL-- [后端]
[用户] --查看历史--> [History API] --> [数据库]
```

### 4.3 改进之处

| 对比项 | 现有方式 | FaceShield |
|--------|----------|------------|
| 检测方式 | 人工 | 模型自动检测 |
| 输出结果 | 主观判断 | 概率+风险等级 |
| 可解释性 | 无 | 热力图+频域/空域分数 |
| 历史记录 | 无 | 数据库持久化 |
| 模型管理 | 无 | 模型版本与选择 |

### 4.4 影响

- **设备**：需要 Web 服务器、数据库和 GPU 训练环境；
- **软件**：Python、Node.js、PaddlePaddle、openGauss；
- **用户**：需具备基本浏览器操作能力；
- **开发**：团队需掌握算法、后端、前端和数据库协作。

### 4.5 局限性

1. 当前为图片级检测，不支持视频；
2. 训练数据主要来自 Deepfakes；
3. 严格 Grad-CAM 仍待完善，当前使用降级热力图保障展示链路；
4. fusion_v2 提升幅度有限，不同 seed 存在波动。

### 4.6 技术条件方面的可行性

1. FaceForensics++ 为公开数据集，可获取；
2. PaddlePaddle 框架成熟，可实现 CNN 训练与推理；
3. FastAPI 与 Vue 生态完善，适合快速开发；
4. 团队成员分工明确，可在学期内完成 MVP。

## 5 可选择的其他系统方案

### 5.1 方案一：仅 RGB baseline，不做频域融合

**优点**：结构简单、训练快、部署容易。  
**未选中原因**：项目目标是验证频域-空域融合思路，仅 baseline 无法体现方法创新性。

### 5.2 方案二：独立算法微服务 + 消息队列

**优点**：解耦更好，适合大规模部署。  
**未选中原因**：MVP 阶段增加复杂度，函数调用即可满足演示需求。

## 6 投资及效益分析

### 6.1 支出

| 类别 | 内容 |
|------|------|
| 硬件 | 开发机、GPU 云服务器（AutoDL） |
| 软件 | 开源框架，无额外授权费用 |
| 人力 | 团队成员开发时间 |
| 数据 | FaceForensics++ 公开数据集 |

### 6.2 收益

1. 形成可演示的伪造人脸检测平台；
2. 完成课程综合实践与答辩材料；
3. 积累深度学习工程化经验；
4. 为后续科研和竞赛提供基础。

## 7 社会因素方面的可行性

### 7.1 法律方面的可行性

系统仅用于学术研究和辅助鉴别演示，不涉及非法采集生物特征数据；用户使用上传图片需遵守相关法律法规。

### 7.2 使用方面的可行性

界面采用中文交互，流程清晰，普通用户经简单说明即可使用。

## 8 结论

经可行性分析，FaceShield 项目在技术上可行、时间上可控、应用上具有现实意义，**可以立即开始并按期完成开发**。

---

# 三、系统开发计划

## 1 引言

本计划用于指导 FaceShield 项目从需求分析到答辩交付的全过程。

## 2 项目概述

### 2.1 工作内容

1. 数据集下载、抽帧、人脸裁剪与 manifest 构建；
2. RGB baseline 与频域-空域融合模型训练；
3. FastAPI 后端、认证、上传、检测、历史接口开发；
4. Vue 前端页面与交互开发；
5. openGauss 表结构设计与 SQL 脚本编写；
6. 系统联调、测试与文档撰写。

### 2.2 主要参加人员

| 成员 | 方向 | 主要负责 |
|------|------|----------|
| 成员 A | 算法 | 数据预处理、模型训练、指标评估 |
| 成员 B | 后端 | FastAPI、算法接入、数据库 |
| 成员 C | 前端 | Vue 页面、交互、接口联调 |
| 成员 D | 数据库 | 表设计、SQL、数据字典 |

（请按实际团队填写）

### 2.3 产品

#### 2.3.1 程序

| 程序 | 语言 | 功能 |
|------|------|------|
| `backend/` | Python | 后端 API 服务 |
| `frontend/` | JavaScript/Vue | Web 前端 |
| `training/` | Python | 模型训练脚本 |
| `tools/` | Python | 数据下载与抽帧 |

#### 2.3.2 文件

- 开发说明书、算法设计文档、实验结果文档；
- openGauss 建表 SQL；
- 用户使用说明与答辩 PPT。

### 2.4 验收标准

1. 用户可登录并完成图片检测全流程；
2. 系统输出伪造概率、风险等级和热力图；
3. 历史记录可查询且用户隔离；
4. fusion_v2 主配置 seed42 达到 test AUC 0.9014、F1 0.8348；
5. 三 seed 平均 test AUC 0.8865、F1 0.8082；
6. 文档齐全，答辩可演示。

### 2.5 完成项目的最迟期限

2026 年 7 月 9 日

## 3 实施计划

### 3.1 工作任务的分解与人员分工

| 阶段 | 时间 | 任务 | 负责人 |
|------|------|------|--------|
| 第 1 阶段 | 5 月 | 数据准备、baseline 训练 | 算法 |
| 第 2 阶段 | 5-6 月 | fusion 模型、后端框架 | 算法+后端 |
| 第 3 阶段 | 6 月 | 前端页面、数据库 | 前端+数据库 |
| 第 4 阶段 | 7 月 | 联调、测试、文档 | 全体 |

### 3.3 进度（里程碑）

| 里程碑 | 目标 |
|--------|------|
| M1 | 数据集与 baseline 训练完成 |
| M2 | fusion_v2 训练完成 |
| M3 | 后端 API 联调通过 |
| M4 | 前端全流程可演示 |
| M5 | 文档与答辩材料完成 |

### 3.5 关键问题

1. 初版 fusion_fft 效果不如 baseline；
2. 热力图生成链路需降级方案保障演示；
3. 前后端字段命名需统一；
4. openGauss 与 SQLite 开发环境差异。

## 4 支持条件

### 4.1 计算机系统支持

- 开发机：Windows 10/11
- GPU 训练：AutoDL RTX 3080 Ti
- 后端运行：Python 3.10+，Uvicorn
- 前端运行：Node.js 18+，Vite 7

---

# 四、系统需求分析

## 2 任务概述

### 2.1 目标

#### 2.1.1 开发意图

构建面向 AI 换脸诈骗场景的伪造人脸检测 Web 系统，实现从图片上传到结果展示的全流程。

#### 2.1.2 应用目标

辅助用户判断上传人脸图片是否存在 DeepFake 伪造痕迹。

#### 2.1.3 产品描述

FaceShield 是一个 B/S 架构 Web 应用，包含首页、登录、检测工作台、结果页、历史记录页。

#### 2.1.4 产品功能

1. 用户认证；
2. 图片上传与模型选择；
3. 伪造检测；
4. 结果可视化；
5. 历史记录管理。

#### 2.1.6 安全性

JWT 鉴权、密码 hash 存储、用户数据隔离。

## 3 具体需求分析

### 3.1 系统流程图

```text
开始 -> 访问首页 -> 开始检测 -> 登录
-> 进入检测工作台 -> 选择模型 -> 上传图片
-> 开始检测 -> 展示结果 -> 保存历史
-> 可继续检测或查看历史 -> 结束
```

### 3.2 数据流图及用例模型

**顶层数据流**：

```text
用户 -> 图片文件 -> FaceShield 系统 -> 检测结果 -> 用户
用户 -> 登录凭证 -> FaceShield 系统 -> Token/历史记录 -> 用户
```

**核心用例**：

| 用例名称 | 参与者 | 目的 |
|----------|--------|------|
| 用户登录 | 用户 | 获取访问令牌 |
| 上传检测 | 用户 | 提交图片并获得检测结果 |
| 查看历史 | 用户 | 查询历史检测记录 |
| 查看详情 | 用户 | 查看单条完整结果 |

（用例详述可按 Word 模板表格补充）

### 3.3 数据字典

#### 数据流条目

| 序号 | 数据流名称 | 来源 | 去向 | 组成 |
|------|------------|------|------|------|
| 1 | 登录请求 | 用户 | 认证模块 | username, password |
| 2 | 检测请求 | 用户 | 检测模块 | file, model_id |
| 3 | 检测结果 | 检测模块 | 前端 | label, fake_probability, risk_level, urls |
| 4 | 历史列表 | 数据库 | 前端 | items[], total |

#### 数据项条目

| 序号 | 数据项 | 类型 | 说明 |
|------|--------|------|------|
| 1 | fake_probability | float | 伪造概率 0~1 |
| 2 | risk_level | string | low/medium/high |
| 3 | label | string | real/fake |
| 4 | model_version | string | 模型版本号 |
| 5 | heatmap_url | string | 热力图路径 |

## 4 支持信息

### 4.1 运行环境

| 层级 | 环境 |
|------|------|
| 客户端 | 现代浏览器 Chrome/Edge |
| Web 服务器 | Uvicorn + FastAPI |
| 数据库 | SQLite（开发）/ openGauss（部署） |
| 算法 | PaddlePaddle 2.4.0，OpenCV |

### 4.2 支持软件

Python 3.10+、Node.js 18+、Vue 3、FastAPI、SQLAlchemy、Axios

### 4.3 接口

- 外部：浏览器 HTTP 请求
- 内部：`predict_image()`、`DetectionService.start_detection()`

## 5 需求分析总结

FaceShield 需求明确，以单图检测为核心，强调可解释展示与历史追溯，技术路线和验收标准清晰，具备实施条件。

---

# 五、系统概要设计

## 2 总体设计

### 2.1 需求规定

见第四章需求分析。

### 2.2 运行环境

**硬件**：

- 客户端：普通 PC
- 服务器：4 核 CPU，8GB+ 内存，可选 GPU

**软件**：

| 组件 | 版本 |
|------|------|
| 操作系统 | Windows 10/11 或 Linux |
| Python | 3.10+ |
| FastAPI | 0.100+ |
| Vue | 3.5 |
| Vite | 7 |
| PaddlePaddle | 2.4.0 |
| 数据库 | SQLite / openGauss |

### 2.3 基本设计概念和处理流程

```text
表现层（Vue 前端）
    ↓ REST API
业务层（FastAPI Services）
    ↓
算法层（Predictor + Paddle/Mock Engine）
    ↓
数据层（SQLAlchemy + openGauss/SQLite）
    ↓
文件层（uploads / crops / heatmaps）
```

### 2.4 软件结构设计

```text
FaceShield/
├── frontend/          前端 Vue 应用
├── backend/           后端 FastAPI 服务
├── training/          模型训练代码
├── model/             部署权重与指标
├── database/          SQL 与 schema
├── docs/              项目文档
└── tools/             数据工具脚本
```

**前端模块**：

- views：home、auth、detective、result、history
- features：auth、detection、history、home
- shared：通用 UI 组件
- stores：auth、detection、history

**后端模块**：

- api：路由层
- services：业务层
- repositories：数据访问层
- algorithm：推理引擎
- models：ORM 实体

### 2.5 功能需求与程序的关系

| 功能 | 前端 | 后端 | 算法 | 数据库 |
|------|------|------|------|--------|
| 登录 | LoginView | auth.service | - | users |
| 检测 | DetectiveView | detection.service | predictor | detection_* |
| 结果 | ResultView | records API | - | detection_result |
| 历史 | HistoryView | history.service | - | detection_* |
| 模型选择 | ModelSelector | model API | engine | model_version |

## 3 接口设计

### 3.1 用户接口

Web 浏览器界面，中文交互。

### 3.2 外部接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/auth/login | POST | 登录 |
| /api/detection/upload-and-detect | POST | 上传检测 |
| /api/records | GET | 历史列表 |
| /api/records/{id} | GET | 记录详情 |
| /api/model-version/list | GET | 模型列表 |
| /api/health | GET | 健康检查 |

### 3.3 内部接口

```python
def predict_image(image_path: str) -> dict
def start_detection(file_id: int, user_id: int, model_id: int | None) -> DetectionResult
```

## 5 系统数据库设计

### 5.1 概念结构设计（E-R 图）

**实体**：

1. User（用户）
2. FileRecord（文件记录）
3. DetectionTask（检测任务）
4. DetectionResult（检测结果）
5. ModelVersion（模型版本）

**联系**：

- User 1:N FileRecord
- User 1:N DetectionTask
- FileRecord 1:1 DetectionTask
- DetectionTask 1:1 DetectionResult
- ModelVersion 关联 DetectionResult（逻辑关联）

（请在 Word 中绘制 E-R 图）

### 5.2 逻辑结构设计

- users(id, username, password_hash, display_name, status, created_at)
- file_record(id, user_id, original_filename, stored_filename, file_url, ...)
- detection_task(id, file_id, user_id, status, ...)
- detection_result(id, task_id, label, fake_probability, risk_level, heatmap_url, ...)
- model_version(id, model_name, version, description, is_active, ...)

### 5.3 物理结构设计

**表 5-1 detection_result 表**

| 序号 | 列名 | 数据类型 | 说明 |
|------|------|----------|------|
| 1 | id | INTEGER | 主键 |
| 2 | task_id | INTEGER | 任务 ID |
| 3 | label | VARCHAR(10) | real/fake |
| 4 | fake_probability | DECIMAL | 伪造概率 |
| 5 | risk_level | VARCHAR(20) | 风险等级 |
| 6 | frequency_score | DECIMAL | 频域分数 |
| 7 | spatial_score | DECIMAL | 空域分数 |
| 8 | heatmap_url | VARCHAR(500) | 热力图路径 |
| 9 | model_name | VARCHAR(100) | 模型名称 |
| 10 | model_version | VARCHAR(50) | 模型版本 |
| 11 | created_at | DATETIME | 检测时间 |

## 6 系统出错处理设计

### 6.1 出错信息

| 错误场景 | 提示 |
|----------|------|
| 未登录 | 401，跳转登录页 |
| 文件格式错误 | 仅支持 JPG/PNG |
| 检测失败 | 检测失败，请稍后重试 |
| 记录不存在 | 404 记录未找到 |

### 6.2 补救措施

1. 前端 InlineError 展示错误；
2. 后端统一异常处理；
3. 检测任务失败时标记 task 状态；
4. 401 自动清理 Token 并跳转登录。

---

# 六、系统详细设计

## 2 程序系统的结构

```text
backend/app/
├── api/                 路由：auth, detection, records, model
├── services/            业务：auth, detection, history, model
├── repositories/        数据访问
├── algorithm/           推理引擎
│   ├── models/          mock_engine, paddle_engine
│   ├── preprocess/      人脸裁剪
│   └── predictor.py     统一推理入口
├── models/              ORM 实体
└── serializers/         响应序列化

frontend/src/
├── views/               页面
├── features/            功能模块
├── shared/              共享组件
└── stores/              状态管理
```

**模块对应关系**：

| 模块 | 说明 | 负责人 |
|------|------|--------|
| auth | 登录认证 | 后端+前端 |
| detection | 上传检测 | 后端+前端+算法 |
| history | 历史记录 | 后端+前端 |
| algorithm | 模型推理 | 算法 |
| database | 表结构与 SQL | 数据库 |

## 3 设计说明

### 3.1 算法训练模块

#### 3.1.1 数据集读取与预处理

- 数据源：FaceForensics++ c23，original + Deepfakes
- 训练 manifest：`face_manifest_clean.csv`
- 样本规模：train 3769 / val 1284 / test 1092
- 输入尺寸：224×224 人脸裁剪图
- 标签：real=0，fake=1
- 数据增强：随机翻转、亮度/对比度扰动
- fusion_fft：完整 FFT 幅度谱
- fusion_v2：高频 FFT，抑制低频干扰

#### 3.1.2 RGB baseline 模型

```text
RGB face crop (3×224×224)
-> TinyBackbone (feature_dim=128)
-> AdaptiveAvgPool2D
-> Dropout(0.3)
-> Linear(128, 2)
-> fake probability
```

作用：建立空域基线，用于对比频域融合收益。

#### 3.1.3 初版频域-空域融合模型 fusion_fft

```text
Spatial branch: RGB -> CNN -> spatial feature
Frequency branch: FFT spectrum -> CNN -> frequency feature
Fusion: concat -> dropout -> linear -> classifier
```

#### 3.1.4 优化后的 fusion_v2 模型

改进点：

1. 高频 FFT 替代全局 FFT；
2. 使用 baseline checkpoint 初始化 spatial branch；
3. gating residual fusion 替代简单 concat；
4. 主配置：freeze-spatial-epochs=3，lr=5e-4。

#### 3.1.5 模型训练与选择

| 参数 | 值 |
|------|-----|
| 框架 | PaddlePaddle 2.4.0 |
| 优化器 | AdamW |
| batch size | 32 |
| weight decay | 0.0001 |
| dropout | 0.3 |
| max epochs | 30 |
| early stopping patience | 8 |
| 模型选择依据 | 验证集 AUC 最优 |

#### 3.1.6 单图推理流程

```text
上传图片 -> 保存原图 -> Haar 人脸检测 -> 1.3倍扩框裁剪
-> resize 224×224 -> predict_image() -> 输出概率与分数
-> 风险等级映射 -> 热力图生成 -> 入库 -> 返回前端
```

### 3.2 后端检测模块

#### 3.2.1 upload_and_detect 接口

- 接收 multipart 文件与 model_id
- 调用 DetectionWorkflowService
- 返回完整 detection result JSON

#### 3.2.2 风险等级策略

| fake_probability | risk_level |
|------------------|------------|
| < 0.4 | low（低风险） |
| 0.4 ~ 0.7 | medium（中风险） |
| >= 0.7 | high（高风险） |

### 3.3 前端模块

| 页面 | 路由 | 功能 |
|------|------|------|
| 首页 | / | Landing、开始检测入口 |
| 登录 | /login | 用户认证 |
| 检测工作台 | /detective | 模型选择、上传、检测 |
| 结果页 | /result/:id | 概率、风险、热力图 |
| 历史记录 | /history | 列表、筛选、分页 |
| 记录详情 | /history/:id | 完整结果 |

## 4 界面设计

主要界面（请在 Word 中插入截图）：

1. 首页 Hero 页
2. 登录页
3. 检测工作台（含模型选择与上传区）
4. 检测结果页（概率环、风险徽章、热力图）
5. 历史记录页

## 5 实现结果

### 5.1 算法实现结果

训练产物：

```text
model/outputs/
├── baseline/best.pdparams
├── fusion_fft/best.pdparams
└── fusion_v2_seed*/best.pdparams

model/deploy/fusion_v2/    部署权重
model/summary/metrics_summary.csv
```

### 5.2 后端实现结果

- FastAPI 分层架构完成
- 支持 mock 与 paddle 双后端
- JWT 认证与用户隔离
- 模型列表与 model_id 检测参数

### 5.3 前端实现结果

- Vue 3 分层前端完成
- 首页、登录、检测、结果、历史全流程
- 伪造概率环形图、风险徽章、热力图展示
- 模型选择下拉框

（核心代码片段可按分工附录粘贴）

---

# 七、系统测试

## 2 测试概要

| 测试项 | 测试内容 |
|--------|----------|
| 功能测试 | 登录、上传、检测、历史、模型选择 |
| 接口测试 | REST API 返回格式与鉴权 |
| 算法测试 | baseline、fusion_fft、fusion_v2 指标 |
| 前端测试 | 页面跳转、loading、错误提示 |
| 安全测试 | 未登录拦截、用户隔离 |

## 3 测试结果及发现

### 3.1 功能测试

| 测试用例 | 输入/动作 | 期望结果 | 实际结果 |
|----------|-----------|----------|----------|
| 正确登录 | demo/demo123456 | 登录成功 | 通过 |
| 错误密码 | 错误凭证 | 登录失败提示 | 通过 |
| 未登录访问 | 直接访问 /detective | 跳转登录 | 通过 |
| 图片上传 | JPG 图片 | 预览正常 | 通过 |
| 开始检测 | 点击检测 | 跳转结果页 | 通过 |
| 历史记录 | 访问 /history | 列表展示 | 通过 |

### 3.2 算法指标测试

**初版模型对比**：

| 模型 | val AUC | test Accuracy | test AUC | F1 |
|------|---------|---------------|----------|-----|
| baseline | 0.8479 | 0.7811 | 0.8554 | 0.7973 |
| fusion_fft | 0.7678 | 0.6941 | 0.7617 | 0.6980 |

**fusion_v2 三 seed 平均**：

| 模型 | Accuracy | AUC | Precision | Recall | F1 |
|------|----------|-----|-----------|--------|-----|
| baseline 平均 | 0.7967 | 0.8805 | 0.7828 | 0.8257 | 0.8025 |
| fusion_v2 平均 | 0.8056 | 0.8865 | 0.7956 | 0.8226 | 0.8082 |

fusion_v2 主配置 seed42：test AUC **0.9014**，F1 **0.8348**。

## 4 对软件功能的结论

### 4.1 检测功能

**能力**：系统已完成图片级伪造人脸检测全流程，可输出概率、风险等级、频域/空域分数和热力图。

**限制**：

1. 当前主要为 Deepfakes 类型；
2. 图片级，不支持视频；
3. Paddle 后端已接入 Grad-CAM 热力图，mock 模式或生成失败时使用 fallback 热力图兜底。

## 5 分析摘要

### 5.1 能力

1. 完成 Web 检测系统 MVP；
2. 完成 RGB baseline 与 fusion_v2 对比实验；
3. fusion_v2 三 seed 平均 AUC、Accuracy、F1 略高于 baseline；
4. 前后端联调通过，可稳定演示。

### 5.2 缺陷和限制

1. 初版 fusion_fft 未超过 baseline；
2. fusion_v2 提升幅度有限，存在 seed 波动；
3. 仅使用 original + Deepfakes；
4. 不含视频级时序检测。

### 5.3 建议

1. 引入 DCT、多尺度 FFT；
2. 尝试 attention 融合；
3. 升级 backbone 为 ResNet18 等；
4. 扩展 Face2Face、FaceSwap 等伪造类型；
5. 继续优化 Grad-CAM 展示质量与错误案例分析。

### 5.4 评价

系统已达到预定 MVP 目标，**可以交付使用**。

## 6 测试资源消耗

| 模型 | 训练耗时 | 设备 |
|------|----------|------|
| baseline | 426.66s | GPU gpu:0 |
| fusion_fft | 681.53s | GPU gpu:0 |
| fusion_v2 seed42 | 713.61s | GPU gpu:0 |

---

# 八、系统用户操作手册

## 1.1 编写目的

指导用户正确使用 FaceShield 进行伪造人脸检测。

## 1.2 适用范围

本手册适用于 FaceShield Web 演示系统。

## 2 安装与卸载

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问：`http://127.0.0.1:5173`

## 3 使用说明

### 3.1 登录

1. 打开系统首页，点击「开始检测」；
2. 输入演示账号：`demo` / `demo123456`；
3. 登录成功后进入检测工作台。

### 3.2 图片检测

1. 在「检测模型」下拉框选择模型；
2. 拖拽或点击上传 JPG/PNG 图片；
3. 点击「开始检测」；
4. 等待分析完成后查看结果页。

### 3.3 查看结果

结果页展示：

- 检测结论（真实/伪造）
- 伪造概率环形图
- 风险等级
- 频域/空域分数
- 原图、人脸裁剪图、热力图

### 3.4 历史记录

1. 点击侧边栏「历史记录」；
2. 可按结论、风险等级筛选；
3. 点击条目查看详情。

---

# 九、总结与展望

FaceShield 项目面向 AI 换脸诈骗场景，完成了基于频域-空域特征融合的伪造人脸检测系统设计与实现。项目实现了数据准备、模型训练、后端服务、前端界面和数据库持久化的完整工程链路。

在算法方面，项目完成了 RGB baseline、初版 fusion_fft 和优化后的 fusion_v2 三类模型实验。实验表明，初版全局 FFT 与简单 concat 融合未能超过 baseline；fusion_v2 通过高频 FFT、baseline 初始化与门控融合，在三组随机种子平均指标上取得了一定提升，可作为当前主模型。

在系统方面，项目实现了用户登录、图片上传、模型选择、检测推理、结果可视化、历史追溯等核心功能，形成了可演示、可答辩、可扩展的 Web 原型系统。

不足之处主要包括：检测粒度仍为图片级；训练数据覆盖的伪造类型有限；fusion_v2 提升幅度不大且存在 seed 波动；热力图可视化仍需进一步完善。

后续工作将从频域特征增强、融合策略优化、backbone 升级、数据集扩展、视频检测和严格 Grad-CAM 等方面继续改进，以提升系统的检测能力、稳定性与实用价值。

---

# 参考文献

[1] Rössler A, Cozzolino D, Verdoliva L, et al. FaceForensics++: Learning to Detect Manipulated Facial Images[C]. ICCV, 2019.

[2] Li Y, Yang X, Wu Y, et al. Face X-ray for More General Face Forgery Detection[C]. CVPR, 2020.

[3] FastAPI Documentation. https://fastapi.tiangolo.com/

[4] Vue.js 3 Documentation. https://vuejs.org/

[5] PaddlePaddle 官方文档. https://www.paddlepaddle.org.cn/

[6] openGauss 数据库文档. https://docs.opengauss.org/

[7] Selvaraju R R, et al. Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization[C]. ICCV, 2017.

[8] FaceShield 项目开发说明书. development_spec.md

[9] FaceShield 算法设计文档. docs/algorithm_design.md

[10] FaceShield 实验结果文档. docs/experiment_results.md

---

# 附录

## 附录 A：团队分工（请填写）

| 序号 | 学号 | 姓名 | 负责模块 |
|------|------|------|----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

## 附录 B：待补充 Word 排版项

1. 封面与团队 Logo
2. E-R 图（Visio/PowerDesigner 绘制）
3. 系统流程图、数据流图、用例图
4. 界面截图（至少 5 个）
5. 训练曲线图（`model/summary/training_curves.svg`）
6. 责任分配矩阵与甘特图
7. 团队沟通纪要与评分表

---

*本文档依据 `FaceShield.doc` 工程项目开发综合实践模板生成，内容来源于 FaceShield 项目实际代码、训练结果与开发文档。复制到 Word 后请按学院格式要求调整字体、行距与页眉页脚。*
