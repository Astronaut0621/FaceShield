下面给你一份适合 **FaceShield 初版项目搭建** 的设计方案。整体目标是：**先把前端、后端、算法模块、MySQL 数据库四部分跑通，形成一个最小可用系统原型**。其中你负责后端，所以后端部分会写得详细一些；前端、算法、数据库只给出基础框架和对接方式。

---

# FaceShield 初版项目设计方案

## 一、项目总体目标

FaceShield 是一个面向 AI 换脸诈骗场景的伪造人脸检测系统。初版系统不追求完整复杂的深度学习训练平台，而是先实现一个清晰的基础流程：

1. 用户在前端上传一张人脸图片；
2. 后端接收图片，保存文件并创建检测任务；
3. 后端调用算法模块进行检测；
4. 算法模块返回检测结果，例如是否疑似伪造、伪造概率、风险等级等；
5. 后端将检测结果写入 MySQL 数据库；
6. 前端展示检测结果和历史记录。

初版重点是把整个业务链路打通，为后续增加视频检测、热力图展示、频域/空域融合模型、用户系统、模型版本管理等功能打基础。

---

# 二、系统总体架构设计

## 2.1 总体架构

系统可以采用典型的前后端分离架构：

```text
前端 Vue
   |
   | HTTP / RESTful API
   |
后端 FastAPI
   |
   | 调用算法服务 / 算法模块
   |
算法模块 Python / PaddlePaddle
   |
   | 数据读写
   |
MySQL 数据库
```

初版可以将后端和算法模块放在同一个 Python 项目中，后端通过函数调用算法模块。等后续算法变复杂后，再拆成独立算法服务。

---

## 2.2 各模块职责

| 模块 | 初版职责 |
|---|---|
| 前端 | 提供图片上传页面、结果展示页面、历史记录页面 |
| 后端 | 提供上传接口、检测接口、历史记录接口、文件管理、数据库交互、算法调用 |
| 算法模块 | 接收图片路径，返回检测结果；初版可先使用模拟结果，后续替换真实模型 |
| 数据库 | 存储上传文件信息、检测任务、检测结果、模型版本等基础数据 |

---

# 三、推荐技术栈

## 3.1 后端技术栈

建议使用：

| 技术 | 作用 |
|---|---|
| Python 3.9+ / 3.10+ | 后端开发语言 |
| FastAPI | Web 后端框架 |
| Uvicorn | ASGI 服务器 |
| SQLAlchemy | ORM 数据库操作 |
| MySQL | 项目数据库 |
| PyMySQL | Python 连接 MySQL |
| Pydantic | 请求参数和响应数据校验 |
| python-multipart | 文件上传支持 |
| OpenCV / Pillow | 图片基础处理 |
| PaddlePaddle | 后续算法模型推理 |
| loguru / logging | 日志记录 |

---

## 3.2 前端技术栈

前端初版建议：

| 技术 | 作用 |
|---|---|
| Vue 3 | 前端框架 |
| Vite | 项目构建工具 |
| Axios | 请求后端接口 |
| Element Plus | UI 组件库 |
| ECharts | 后续可视化图表或风险展示 |

---

## 3.3 算法模块技术栈

算法初版建议：

| 技术 | 作用 |
|---|---|
| Python | 算法开发语言 |
| PaddlePaddle | 模型训练和推理 |
| OpenCV | 图像读取、预处理 |
| NumPy | 数值计算 |
| Matplotlib / OpenCV | 后续生成热力图 |

初版算法可以先写一个假推理函数，随机返回结果，保证后端接口先跑通。

---

# 四、后端详细设计

## 4.1 后端核心职责

后端是整个系统的业务中心，主要负责：

1. 接收前端上传的图片；
2. 校验上传文件是否合法；
3. 将图片保存到本地文件目录；
4. 在数据库中创建检测任务；
5. 调用算法模块进行伪造人脸检测；
6. 接收算法模块返回的检测结果；
7. 将检测结果保存到数据库；
8. 向前端返回检测报告；
9. 提供历史记录查询接口；
10. 提供单条检测详情查询接口；
11. 后续扩展用户管理、模型版本管理、视频检测等功能。

---

## 4.2 后端项目目录结构

建议后端项目目录如下：

```text
faceshield-backend/
│
├── app/
│   ├── main.py                     # FastAPI 入口文件
│   │
│   ├── core/                       # 核心配置
│   │   ├── config.py               # 配置文件
│   │   ├── database.py             # 数据库连接
│   │   └── logger.py               # 日志配置
│   │
│   ├── api/                        # API 路由层
│   │   ├── __init__.py
│   │   ├── upload.py               # 图片上传接口
│   │   ├── detection.py            # 检测接口
│   │   └── history.py              # 历史记录接口
│   │
│   ├── models/                     # 数据库模型
│   │   ├── __init__.py
│   │   ├── detection_task.py       # 检测任务表模型
│   │   ├── detection_result.py     # 检测结果表模型
│   │   ├── file_record.py          # 文件记录表模型
│   │   └── model_version.py        # 模型版本表模型
│   │
│   ├── schemas/                    # Pydantic 数据结构
│   │   ├── __init__.py
│   │   ├── detection_schema.py
│   │   ├── history_schema.py
│   │   └── common_schema.py
│   │
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── file_service.py         # 文件保存、校验
│   │   ├── detection_service.py    # 检测业务逻辑
│   │   └── history_service.py      # 历史记录业务逻辑
│   │
│   ├── algorithm/                  # 算法模块适配层
│   │   ├── __init__.py
│   │   ├── predictor.py            # 后端调用算法的统一入口
│   │   └── mock_predictor.py       # 初版模拟算法
│   │
│   ├── utils/                      # 工具函数
│   │   ├── __init__.py
│   │   ├── response.py             # 统一响应格式
│   │   ├── file_utils.py           # 文件工具
│   │   └── time_utils.py           # 时间工具
│   │
│   └── static/                     # 静态资源访问目录，可选
│
├── storage/                        # 上传文件和检测结果存储
│   ├── uploads/                    # 用户上传图片
│   ├── reports/                    # 检测报告
│   └── heatmaps/                   # 后续热力图
│
├── requirements.txt                # 后端依赖
├── README.md
└── run.py                          # 启动文件，可选
```

这个结构比较适合课程项目，层次清楚，后续扩展方便。

---

# 五、后端功能模块设计

## 5.1 文件上传模块

### 功能说明

文件上传模块负责接收前端传来的图片文件，并完成：

1. 文件类型检查；
2. 文件大小检查；
3. 文件重命名；
4. 文件保存；
5. 生成文件访问路径；
6. 向数据库写入文件记录。

---

### 支持的文件类型

初版建议支持：

```text
.jpg
.jpeg
.png
.bmp
```

暂时不建议一开始支持视频，因为视频检测涉及抽帧、帧级检测、结果聚合，工作量会明显增加。

---

### 文件大小限制

初版可以限制为：

```text
单张图片最大 10MB
```

后续再根据实际情况调整。

---

### 文件命名方式

建议不要直接使用用户上传的原始文件名，而是使用 UUID 防止重名：

```text
20250601_153000_550e8400-e29b-41d4-a716-446655440000.jpg
```

---

### 上传流程

```text
前端选择图片
   |
调用 POST /api/files/upload
   |
后端校验图片类型和大小
   |
保存到 storage/uploads/
   |
写入 file_record 表
   |
返回 file_id 和 file_url
```

---

## 5.2 检测任务模块

检测任务模块是后端的核心业务模块。

### 功能说明

用户上传图片后，可以发起检测任务。检测任务模块负责：

1. 根据 file_id 找到对应图片；
2. 创建检测任务记录；
3. 调用算法模块；
4. 获取检测结果；
5. 生成风险等级；
6. 保存检测结果；
7. 更新任务状态；
8. 返回检测报告。

---

### 任务状态设计

检测任务可以设计以下状态：

| 状态 | 含义 |
|---|---|
| pending | 等待检测 |
| running | 检测中 |
| success | 检测成功 |
| failed | 检测失败 |

初版可以同步检测，即用户一请求，后端立即调用算法，然后返回结果。后续如果模型推理耗时较长，可以改成异步任务。

---

### 检测流程

```text
前端调用检测接口
   |
后端根据 file_id 查询图片
   |
创建 detection_task，状态为 pending
   |
更新状态为 running
   |
调用 algorithm.predict(image_path)
   |
算法返回 fake_probability、label、confidence 等信息
   |
后端生成风险等级
   |
写入 detection_result 表
   |
更新 detection_task 状态为 success
   |
返回检测结果
```

---

## 5.3 检测结果模块

### 检测结果内容

初版检测结果建议包含：

| 字段 | 说明 |
|---|---|
| task_id | 检测任务 ID |
| file_id | 文件 ID |
| label | 检测标签，例如 real / fake |
| fake_probability | 伪造概率 |
| confidence | 模型置信度 |
| risk_level | 风险等级 |
| model_name | 使用的模型名称 |
| model_version | 模型版本 |
| heatmap_url | 可疑区域热力图，初版可为空 |
| frequency_score | 频域异常分数，初版可为空或模拟 |
| spatial_score | 空域异常分数，初版可为空或模拟 |
| suggestion | 系统提示建议 |

---

## 5.4 历史记录模块

### 功能说明

历史记录模块用于查看过往检测结果，方便前端展示。

初版提供：

1. 查询检测历史列表；
2. 查看单条检测详情；
3. 按检测结果筛选；
4. 按时间排序；
5. 删除检测记录，可选。

---

### 历史记录展示字段

| 字段 | 说明 |
|---|---|
| task_id | 检测任务编号 |
| filename | 原始文件名 |
| label | 检测结果 |
| fake_probability | 伪造概率 |
| risk_level | 风险等级 |
| created_at | 检测时间 |

---

## 5.5 模型调用模块

### 初版建议

初版不要一开始就把真实模型接进来，否则后端开发会被算法进度卡住。

建议先在后端写一个算法适配层：

```text
app/algorithm/predictor.py
```

这个文件对外只提供一个统一函数：

```python
predict_image(image_path: str) -> dict
```

后端永远只调用这个函数。

初版里面可以先使用 mock 结果：

```python
{
    "label": "fake",
    "fake_probability": 0.8732,
    "confidence": 0.91,
    "risk_level": "high",
    "frequency_score": 0.82,
    "spatial_score": 0.76,
    "heatmap_path": None,
    "model_name": "FaceShield-MockNet",
    "model_version": "v0.1"
}
```

等算法人员完成真实模型后，只需要修改 `predictor.py` 内部逻辑，不影响后端接口。

---

# 六、后端 API 接口设计

## 6.1 统一接口返回格式

建议所有接口统一返回：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

错误时：

```json
{
  "code": 400,
  "message": "文件格式不支持",
  "data": null
}
```

这样前端处理会比较方便。

---

## 6.2 文件上传接口

### 接口说明

上传待检测图片。

### 请求方式

```http
POST /api/files/upload
```

### 请求参数

使用 `multipart/form-data`：

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| file | File | 是 | 上传图片 |

### 返回示例

```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "file_id": 1,
    "original_filename": "test.jpg",
    "stored_filename": "20250601_153000_uuid.jpg",
    "file_url": "/storage/uploads/20250601_153000_uuid.jpg"
  }
}
```

---

## 6.3 发起检测接口

### 接口说明

根据上传文件 ID 发起检测。

### 请求方式

```http
POST /api/detection/start
```

### 请求体

```json
{
  "file_id": 1
}
```

### 返回示例

```json
{
  "code": 200,
  "message": "检测完成",
  "data": {
    "task_id": 1001,
    "file_id": 1,
    "label": "fake",
    "fake_probability": 0.8732,
    "confidence": 0.91,
    "risk_level": "high",
    "frequency_score": 0.82,
    "spatial_score": 0.76,
    "heatmap_url": null,
    "suggestion": "该图片存在较高伪造风险，请谨慎判断其真实性。",
    "model_name": "FaceShield-MockNet",
    "model_version": "v0.1",
    "created_at": "2026-07-05 15:30:00"
  }
}
```

---

## 6.4 上传并立即检测接口

为了前端方便，也可以额外提供一个一体化接口。

### 请求方式

```http
POST /api/detection/upload-and-detect
```

### 请求参数

`multipart/form-data`：

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| file | File | 是 | 上传图片 |

### 说明

这个接口内部完成：

```text
上传文件 -> 保存文件 -> 创建任务 -> 调用算法 -> 返回结果
```

非常适合初版演示使用。

---

## 6.5 查询历史记录接口

### 请求方式

```http
GET /api/history/list
```

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 10 |
| label | string | 否 | real / fake |
| risk_level | string | 否 | low / medium / high |

### 返回示例

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 2,
    "items": [
      {
        "task_id": 1001,
        "file_id": 1,
        "original_filename": "test.jpg",
        "label": "fake",
        "fake_probability": 0.8732,
        "risk_level": "high",
        "created_at": "2026-07-05 15:30:00"
      }
    ]
  }
}
```

---

## 6.6 查询检测详情接口

### 请求方式

```http
GET /api/history/{task_id}
```

### 返回示例

```json
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "task_id": 1001,
    "file_id": 1,
    "original_filename": "test.jpg",
    "file_url": "/storage/uploads/20250601_153000_uuid.jpg",
    "label": "fake",
    "fake_probability": 0.8732,
    "confidence": 0.91,
    "risk_level": "high",
    "frequency_score": 0.82,
    "spatial_score": 0.76,
    "heatmap_url": null,
    "suggestion": "该图片存在较高伪造风险，请谨慎判断其真实性。",
    "model_name": "FaceShield-MockNet",
    "model_version": "v0.1",
    "created_at": "2026-07-05 15:30:00"
  }
}
```

---

## 6.7 健康检查接口

### 请求方式

```http
GET /api/health
```

### 返回示例

```json
{
  "code": 200,
  "message": "FaceShield backend is running",
  "data": {
    "status": "ok"
  }
}
```

这个接口用于确认后端是否启动成功。

---

# 七、MySQL 数据库设计

初版数据库不要设计太复杂，建议先建 4 张核心表：

1. 文件记录表：`file_record`
2. 检测任务表：`detection_task`
3. 检测结果表：`detection_result`
4. 模型版本表：`model_version`

---

## 7.1 文件记录表 file_record

用于保存用户上传的文件信息。

```sql
CREATE TABLE file_record (
    id SERIAL PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 文件 ID |
| original_filename | 原始文件名 |
| stored_filename | 系统保存后的文件名 |
| file_path | 文件在服务器上的实际路径 |
| file_url | 前端访问路径 |
| file_type | 文件类型 |
| file_size | 文件大小 |
| upload_time | 上传时间 |
| is_deleted | 是否逻辑删除 |

---

## 7.2 检测任务表 detection_task

用于记录每一次检测任务。

```sql
CREATE TABLE detection_task (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL,
    task_status VARCHAR(50) DEFAULT 'pending',
    task_type VARCHAR(50) DEFAULT 'image',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    CONSTRAINT fk_detection_task_file
        FOREIGN KEY (file_id)
        REFERENCES file_record(id)
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 任务 ID |
| file_id | 对应上传文件 ID |
| task_status | pending / running / success / failed |
| task_type | image / video |
| error_message | 检测失败时的错误信息 |
| created_at | 创建时间 |
| started_at | 开始检测时间 |
| finished_at | 检测完成时间 |

---

## 7.3 检测结果表 detection_result

用于保存算法检测结果。

```sql
CREATE TABLE detection_result (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    label VARCHAR(50),
    fake_probability NUMERIC(6, 4),
    confidence NUMERIC(6, 4),
    risk_level VARCHAR(50),
    frequency_score NUMERIC(6, 4),
    spatial_score NUMERIC(6, 4),
    heatmap_url VARCHAR(500),
    suggestion TEXT,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detection_result_task
        FOREIGN KEY (task_id)
        REFERENCES detection_task(id),
    CONSTRAINT fk_detection_result_file
        FOREIGN KEY (file_id)
        REFERENCES file_record(id)
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 检测结果 ID |
| task_id | 任务 ID |
| file_id | 文件 ID |
| label | real / fake |
| fake_probability | 伪造概率 |
| confidence | 模型置信度 |
| risk_level | low / medium / high |
| frequency_score | 频域异常分数 |
| spatial_score | 空域异常分数 |
| heatmap_url | 热力图路径 |
| suggestion | 检测建议 |
| model_name | 模型名称 |
| model_version | 模型版本 |
| created_at | 创建时间 |

---

## 7.4 模型版本表 model_version

用于后续记录不同模型版本。

```sql
CREATE TABLE model_version (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    model_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

字段说明：

| 字段 | 说明 |
|---|---|
| id | 模型版本 ID |
| model_name | 模型名称 |
| version | 模型版本 |
| description | 模型说明 |
| model_path | 模型文件路径 |
| is_active | 是否当前启用 |
| created_at | 创建时间 |

---

## 7.5 初始模型版本数据

可以插入一条模拟模型数据：

```sql
INSERT INTO model_version (
    model_name,
    version,
    description,
    model_path,
    is_active
) VALUES (
    'FaceShield-MockNet',
    'v0.1',
    '初版模拟检测模型，用于前后端联调',
    NULL,
    TRUE
);
```

---

# 八、后端关键业务流程设计

## 8.1 图片上传流程

```text
1. 前端提交图片文件
2. 后端检查文件是否为空
3. 后端检查文件后缀是否合法
4. 后端检查文件大小是否超过限制
5. 后端生成新的文件名
6. 后端将文件保存到 storage/uploads/
7. 后端将文件信息写入 file_record 表
8. 后端返回 file_id 和 file_url
```

---

## 8.2 图片检测流程

```text
1. 前端传入 file_id
2. 后端查询 file_record 表，确认文件存在
3. 后端创建 detection_task 记录，状态为 pending
4. 后端更新任务状态为 running
5. 后端调用算法模块 predict_image(image_path)
6. 算法模块返回检测结果
7. 后端根据 fake_probability 生成风险等级和提示语
8. 后端写入 detection_result 表
9. 后端更新 detection_task 状态为 success
10. 后端向前端返回检测结果
```

---

## 8.3 检测失败流程

如果算法模块报错或文件不存在：

```text
1. 后端捕获异常
2. 更新 detection_task 状态为 failed
3. 记录 error_message
4. 返回错误信息给前端
```

返回示例：

```json
{
  "code": 500,
  "message": "检测失败，请稍后重试",
  "data": null
}
```

---

# 九、风险等级设计

为了便于前端展示，可以根据伪造概率划分风险等级。

```text
fake_probability < 0.4        low
0.4 <= fake_probability < 0.7 medium
fake_probability >= 0.7       high
```

中文含义：

| 风险等级 | 含义 | 展示建议 |
|---|---|---|
| low | 低风险 | 绿色 |
| medium | 中风险 | 橙色 |
| high | 高风险 | 红色 |

---

## 9.1 建议提示语设计

后端可以根据风险等级生成提示语。

### low

```text
该图片暂未发现明显伪造风险，但检测结果仅供参考。
```

### medium

```text
该图片存在一定伪造风险，建议结合来源和上下文进一步判断。
```

### high

```text
该图片存在较高伪造风险，请谨慎判断其真实性，避免被用于身份冒充或诈骗场景。
```

---

# 十、算法模块基础框架

算法模块初版只需要给后端提供统一调用入口。

## 10.1 算法目录结构

```text
app/algorithm/
│
├── __init__.py
├── predictor.py          # 统一调用入口
├── mock_predictor.py     # 模拟算法
├── preprocess.py         # 图像预处理，后续使用
├── frequency_feature.py  # 频域特征提取，后续使用
├── spatial_feature.py    # 空域特征提取，后续使用
└── model_loader.py       # 模型加载，后续使用
```

---

## 10.2 初版算法接口

后端只需要调用：

```python
predict_image(image_path: str) -> dict
```

返回格式建议固定：

```python
{
    "label": "fake",
    "fake_probability": 0.8732,
    "confidence": 0.91,
    "risk_level": "high",
    "frequency_score": 0.82,
    "spatial_score": 0.76,
    "heatmap_path": None,
    "model_name": "FaceShield-MockNet",
    "model_version": "v0.1"
}
```

这样以后真实算法上线时，后端不用改接口。

---

# 十一、前端基础框架

前端初版只需要实现 3 个页面：

```text
1. 首页 / 图片上传页
2. 检测结果页
3. 历史记录页
```

---

## 11.1 前端目录结构

```text
faceshield-frontend/
│
├── src/
│   ├── api/
│   │   ├── request.js          # axios 封装
│   │   ├── detection.js        # 检测接口
│   │   └── history.js          # 历史记录接口
│   │
│   ├── views/
│   │   ├── UploadView.vue      # 上传检测页
│   │   ├── ResultView.vue      # 结果展示页
│   │   └── HistoryView.vue     # 历史记录页
│   │
│   ├── components/
│   │   ├── FileUploader.vue    # 上传组件
│   │   └── ResultCard.vue      # 检测结果卡片
│   │
│   ├── router/
│   │   └── index.js
│   │
│   ├── App.vue
│   └── main.js
│
├── package.json
└── vite.config.js
```

---

## 11.2 前端初版页面功能

### 上传检测页

功能：

1. 选择图片；
2. 预览图片；
3. 点击“开始检测”；
4. 调用后端接口；
5. 跳转或展示检测结果。

---

### 检测结果页

展示内容：

1. 原图；
2. 检测结论；
3. 伪造概率；
4. 风险等级；
5. 频域异常分数；
6. 空域异常分数；
7. 系统提示语。

---

### 历史记录页

展示内容：

1. 检测时间；
2. 文件名；
3. 检测结果；
4. 风险等级；
5. 伪造概率；
6. 查看详情按钮。

---

# 十二、后端开发优先级建议

你负责后端，可以按照下面顺序开发，不容易乱。

## 第一阶段：后端基础工程搭建

先完成：

1. FastAPI 项目创建；
2. 配置文件管理；
3. 数据库连接；
4. 健康检查接口；
5. 统一响应格式；
6. CORS 跨域配置。

目标：后端能启动，前端能访问 `/api/health`。

---

## 第二阶段：数据库模型搭建

完成：

1. file_record 表；
2. detection_task 表；
3. detection_result 表；
4. model_version 表；
5. SQLAlchemy 模型；
6. 数据库连接测试。

目标：后端可以正常读写 MySQL。

---

## 第三阶段：文件上传接口

完成：

1. 文件类型校验；
2. 文件大小校验；
3. 文件保存；
4. 文件记录入库；
5. 返回 file_id。

目标：前端可以上传图片，数据库能看到记录。

---

## 第四阶段：算法适配层

完成：

1. `predict_image(image_path)` 函数；
2. mock 检测结果；
3. 固定返回格式。

目标：后端能调用算法模块并拿到结果。

---

## 第五阶段：检测接口

完成：

1. 根据 file_id 查询图片；
2. 创建检测任务；
3. 调用算法；
4. 保存检测结果；
5. 返回检测报告。

目标：上传图片后可以完成一次完整检测。

---

## 第六阶段：历史记录接口

完成：

1. 历史列表查询；
2. 检测详情查询；
3. 分页；
4. 按风险等级筛选。

目标：前端可以展示历史检测记录。

---

# 十三、后端初版接口清单

建议你先实现这些接口：

| 接口 | 方法 | 功能 |
|---|---|---|
| `/api/health` | GET | 健康检查 |
| `/api/files/upload` | POST | 上传图片 |
| `/api/detection/start` | POST | 根据 file_id 发起检测 |
| `/api/detection/upload-and-detect` | POST | 上传并立即检测 |
| `/api/history/list` | GET | 查询历史记录 |
| `/api/history/{task_id}` | GET | 查询检测详情 |

这 6 个接口足够支撑初版演示。

---

# 十四、部署和运行建议

## 14.1 后端运行方式

后端开发阶段可以使用：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：

```text
http://localhost:8000
```

接口文档：

```text
http://localhost:8000/docs
```

FastAPI 自动生成接口文档，这对你们联调很方便。

---

## 14.2 前端运行方式

```bash
npm install
npm run dev
```

前端默认访问：

```text
http://localhost:5173
```

---

## 14.3 数据库运行

MySQL 可以本地安装，也可以使用 Docker 或实验室数据库环境。

后端连接配置建议写到 `.env` 或 `config.py` 中，例如：

```text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=faceshield_db
DB_USER=faceshield_user
DB_PASSWORD=your_password
```

SQLAlchemy 连接形式可以参考 MySQL 写法：

```text
mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

---

# 十五、初版最小闭环

最终你们第一版系统只要能够做到下面这个闭环，就已经是一个合格的基础框架：

```text
前端上传图片
   ↓
后端保存图片
   ↓
后端写入文件记录
   ↓
后端创建检测任务
   ↓
后端调用算法 mock 模块
   ↓
算法返回检测结果
   ↓
后端保存检测结果
   ↓
前端展示伪造概率和风险等级
   ↓
用户可以查看历史记录
```

---

# 十六、后续扩展方向

等初版跑通之后，可以逐步扩展：

1. 接入真实频域-空域融合模型；
2. 增加人脸检测和裁剪；
3. 增加热力图展示；
4. 支持视频上传和抽帧检测；
5. 增加批量检测；
6. 增加用户登录和权限管理；
7. 增加模型版本切换；
8. 增加检测报告导出；
9. 增加数据集管理；
10. 增加检测结果统计分析。

---

# 十七、总结

FaceShield 初版建议采用 **Vue + FastAPI + Python 算法模块 + MySQL** 的结构。后端作为核心中间层，负责文件处理、任务管理、算法调用、数据库交互和结果返回。

你作为后端开发人员，优先要完成的是：

1. FastAPI 基础框架；
2. MySQL 数据库连接；
3. 文件上传接口；
4. 检测任务接口；
5. 算法模块调用接口；
6. 历史记录查询接口。

前端和算法模块初期都可以先做最小实现，保证系统能完整跑通。这样项目结构清楚、职责明确，后续无论是接入真实模型，还是增加视频检测和热力图展示，都比较容易扩展。
