markdown
# MySQL 数据库配置与使用说明

## 1. 数据库概述

| 项目 | 内容 |
|------|------|
| 数据库类型 | MySQL 8.4.10 LTS |
| 数据库名称 | faceshield_db |
| 字符集 | utf8mb4 |
| 排序规则 | utf8mb4_unicode_ci |
| 部署环境 | Windows 本地开发环境 |
| 服务名称 | MySQL84 |

## 2. 数据库连接信息

### 2.1 连接参数

| 参数 | 值 |
|------|-----|
| 主机地址 | localhost（本机开发）/ 172.20.10.3（远程开发） |
| 端口 | 3306 |
| 数据库名 | faceshield_db |
| 用户名 | faceshield_user |
| 密码 | Faceshield@2026 |

### 2.2 DATABASE_URL 连接字符串

```env
DATABASE_URL=mysql+pymysql://faceshield_user:Faceshield@2026@localhost:3306/faceshield_db?charset=utf8mb4
2.3 Python 代码连接示例
python
import pymysql

# 方式一：使用 PyMySQL
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='faceshield_user',
    password='Faceshield@2026',
    database='faceshield_db',
    charset='utf8mb4'
)

# 方式二：使用 SQLAlchemy
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://faceshield_user:Faceshield@2026@localhost:3306/faceshield_db?charset=utf8mb4"
engine = create_engine(DATABASE_URL)
3. 数据库结构
3.1 表清单
表名	说明
users	用户账户信息
file_record	上传文件记录
detection_task	检测任务状态追踪
detection_result	检测结果详情
model_version	模型版本管理
detection_records（视图）	检测记录联表查询视图
3.2 E-R 关系图
text
users (1) ─────── (N) file_record
   │                     │
   │                     │
   └─ (N) detection_task (1) ─────── (1) detection_result
3.3 视图说明
detection_records 视图将 detection_result、file_record、detection_task 三张表的关键字段关联拼接，提供统一的历史记录查询接口。前端/后端只需执行单表查询即可获取完整检测记录。

4. 常用操作
4.1 连接数据库
bash
mysql -u faceshield_user -p -h localhost -P 3306
输入密码 Faceshield@2026 后进入 MySQL 命令行。

4.2 查看所有表
sql
USE faceshield_db;
SHOW TABLES;
4.3 查看检测记录视图
sql
SELECT * FROM detection_records ORDER BY created_at DESC LIMIT 10;
4.4 统计检测概览
sql
SELECT
    COUNT(*) AS total_detections,
    SUM(CASE WHEN prediction = 'fake' THEN 1 ELSE 0 END) AS fake_count,
    SUM(CASE WHEN prediction = 'real' THEN 1 ELSE 0 END) AS real_count,
    ROUND(AVG(fake_probability), 4) AS avg_fake_prob
FROM detection_records;
5. 备份与恢复
5.1 备份命令
bash
mysqldump -u faceshield_user -p faceshield_db > backup_$(date +%Y%m%d).sql
5.2 恢复命令
bash
mysql -u faceshield_user -p faceshield_db < backup_20260708.sql
5.3 Windows 定时备份脚本
详见 scripts/backup.bat。

6. 安全注意事项
密码加密：users.password_hash 存储 bcrypt/argon2 哈希值，不存明文密码

用户数据隔离：所有查询历史记录的 SQL 必须带 user_id 条件

非 root 账号：应用使用 faceshield_user 连接数据库，不使用 root

配置文件管理：真实密码放在 .env 文件中，.gitignore 排除，不提交至 GitHub

远程访问：仅开发环境开放远程连接（faceshield_user@%），生产环境应限制为 localhost

markdown
# FaceShield 数据字典

**数据库名称**：faceshield_db  
**数据库类型**：MySQL 8.4.10 LTS  
**字符集**：utf8mb4  
**最后更新**：2026年7月8日


## 一、E-R图
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ users │ │ file_record │ │ detection_task │ │ detection_result│
├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ id (PK) │◄─────────│ user_id (FK) │ │ id (PK) │ │ id (PK) │
│ username │ │ id (PK) │◄─────────│ file_id (FK) │ │ user_id (FK) │
│ password_hash │ │ original_filename│ │ user_id (FK) │◄─────────│ task_id (FK) │
│ display_name │ │ stored_filename │ │ task_status │ │ file_id (FK) │
│ status │ │ image_hash │ │ task_type │ │ label │
│ created_at │ │ file_path │ │ error_message │ │ fake_probability│
│ last_login_at │ │ file_url │ │ created_at │ │ confidence │
└─────────────────┘ │ file_type │ │ started_at │ │ risk_level │
│ file_size │ │ finished_at │ │ frequency_score │
│ upload_time │ └─────────────────┘ │ spatial_score │
│ is_deleted │ │ heatmap_url │
└─────────────────┘ │ face_crop_url │
│ face_detected │
│ suggestion │
│ model_name │
│ model_version │
│ created_at │
└─────────────────┘

┌─────────────────┐
│ model_version │
├─────────────────┤
│ id (PK) │
│ model_name │
│ version │
│ description │
│ model_path │
│ is_active │
│ created_at │
└─────────────────┘

关系说明：
users 1 ──┐── N file_record (一个用户可上传多个文件)
users 1 ──┴── N detection_result (一个用户可拥有多条检测结果)
file_record 1 ── N detection_task (一个文件可对应多个检测任务)
detection_task 1 ── 1 detection_result (一个任务只有一个检测结果)

text


## 二、表结构详细说明

### 2.1 表名：users（用户表）

**业务含义**：存储系统用户的基本信息，用于身份认证和权限管理。

| 字段名 | 类型 | 允许空 | 默认值 | 约束 | 说明 |
|--------|------|--------|--------|------|------|
| id | INT | 否 | AUTO_INCREMENT | PRIMARY KEY | 用户唯一标识 |
| username | VARCHAR(100) | 否 | 无 | UNIQUE | 用户名，用于登录 |
| password_hash | VARCHAR(255) | 否 | 无 | | 密码哈希值（bcrypt加密） |
| display_name | VARCHAR(100) | 是 | NULL | | 用户显示昵称 |
| status | VARCHAR(50) | 是 | 'active' | | 账户状态：active/disabled |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | | 注册时间 |
| last_login_at | TIMESTAMP | 是 | NULL | | 最后登录时间 |

### 2.2 表名：file_record（文件记录表）

**业务含义**：记录用户上传的所有文件信息，是检测任务的数据源头。

| 字段名 | 类型 | 允许空 | 默认值 | 约束 | 说明 |
|--------|------|--------|--------|------|------|
| id | INT | 否 | AUTO_INCREMENT | PRIMARY KEY | 文件唯一标识 |
| user_id | INT | 是 | NULL | FOREIGN KEY | 上传者ID，关联users.id |
| original_filename | VARCHAR(255) | 否 | 无 | | 用户上传时的原始文件名 |
| stored_filename | VARCHAR(255) | 否 | 无 | UNIQUE | 系统生成的唯一存储文件名 |
| image_hash | VARCHAR(128) | 是 | NULL | | 图片SHA-256哈希值 |
| file_path | VARCHAR(500) | 否 | 无 | | 文件在服务器上的存储路径 |
| file_url | VARCHAR(500) | 是 | NULL | | 文件访问URL |
| file_type | VARCHAR(50) | 是 | NULL | | 文件类型：jpg/png |
| file_size | BIGINT | 是 | NULL | | 文件大小（字节） |
| upload_time | TIMESTAMP | 是 | CURRENT_TIMESTAMP | | 上传时间 |
| is_deleted | BOOLEAN | 是 | FALSE | | 软删除标记 |

### 2.3 表名：detection_task（检测任务表）

**业务含义**：跟踪每次检测任务的执行状态和进度。

| 字段名 | 类型 | 允许空 | 默认值 | 约束 | 说明 |
|--------|------|--------|--------|------|------|
| id | INT | 否 | AUTO_INCREMENT | PRIMARY KEY | 任务唯一标识 |
| user_id | INT | 是 | NULL | FOREIGN KEY | 发起用户ID，关联users.id |
| file_id | INT | 否 | 无 | FOREIGN KEY | 关联文件ID，关联file_record.id |
| task_status | VARCHAR(50) | 是 | 'pending' | | pending/running/completed/failed |
| task_type | VARCHAR(50) | 是 | 'image' | | 任务类型：image |
| error_message | TEXT | 是 | NULL | | 任务失败时的错误信息 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | | 任务创建时间 |
| started_at | TIMESTAMP | 是 | NULL | | 任务开始处理时间 |
| finished_at | TIMESTAMP | 是 | NULL | | 任务完成时间 |

### 2.4 表名：detection_result（检测结果表）

**业务含义**：存储模型检测的完整结果，是系统的核心数据产出表。

| 字段名 | 类型 | 允许空 | 默认值 | 约束 | 说明 |
|--------|------|--------|--------|------|------|
| id | INT | 否 | AUTO_INCREMENT | PRIMARY KEY | 结果唯一标识 |
| user_id | INT | 是 | NULL | FOREIGN KEY | 用户ID，关联users.id |
| task_id | INT | 否 | 无 | FOREIGN KEY | 关联任务ID，关联detection_task.id |
| file_id | INT | 否 | 无 | FOREIGN KEY | 关联文件ID，关联file_record.id |
| label | VARCHAR(50) | 是 | NULL | | real（真实）/ fake（伪造） |
| fake_probability | DECIMAL(6,4) | 是 | NULL | | 伪造概率（0~1） |
| confidence | DECIMAL(6,4) | 是 | NULL | | 综合置信度（0~1） |
| risk_level | VARCHAR(50) | 是 | NULL | | low / medium / high |
| frequency_score | DECIMAL(6,4) | 是 | NULL | | 频域分支得分 |
| spatial_score | DECIMAL(6,4) | 是 | NULL | | 空域分支得分 |
| heatmap_url | VARCHAR(500) | 是 | NULL | | Grad-CAM热力图访问URL |
| face_crop_url | VARCHAR(500) | 是 | NULL | | 裁剪人脸图URL |
| face_detected | BOOLEAN | 是 | FALSE | | 是否检测到人脸 |
| suggestion | TEXT | 是 | NULL | | 检测建议文本 |
| model_name | VARCHAR(100) | 是 | NULL | | 使用的模型名称 |
| model_version | VARCHAR(50) | 是 | NULL | | 使用的模型版本号 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | | 检测时间 |

### 2.5 表名：model_version（模型版本表）

**业务含义**：管理检测模型的版本信息，支持模型迭代和溯源。

| 字段名 | 类型 | 允许空 | 默认值 | 约束 | 说明 |
|--------|------|--------|--------|------|------|
| id | INT | 否 | AUTO_INCREMENT | PRIMARY KEY | 版本唯一标识 |
| model_name | VARCHAR(100) | 否 | 无 | | 模型名称 |
| version | VARCHAR(50) | 否 | 无 | | 版本号 |
| description | TEXT | 是 | NULL | | 版本描述 |
| model_path | VARCHAR(500) | 是 | NULL | | 模型文件存储路径 |
| is_active | BOOLEAN | 是 | FALSE | | 是否为当前激活版本 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | | 发布时间 |


## 三、视图：detection_records

**业务含义**：将 detection_result、file_record、detection_task 三张表关联，提供统一的历史记录查询接口。

| 字段名 | 来源 | 说明 |
|--------|------|------|
| id | detection_task.id | 任务ID |
| user_id | detection_result.user_id | 用户ID |
| image_hash | file_record.image_hash | 图片哈希值 |
| original_image_path | file_record.file_path | 原图存储路径 |
| face_crop_path | detection_result.face_crop_url | 裁剪人脸图URL |
| heatmap_path | detection_result.heatmap_url | 热力图URL |
| prediction | detection_result.label | 检测标签（real/fake） |
| fake_probability | detection_result.fake_probability | 伪造概率 |
| risk_level | detection_result.risk_level | 风险等级 |
| model_version | detection_result.model_version | 模型版本 |
| face_detected | detection_result.face_detected | 是否检测到人脸 |
| created_at | detection_result.created_at | 检测时间 |


## 四、存储策略说明

### 为什么图片/热力图/模型文件不直接存入 MySQL？

| 方式 | 优点 | 缺点 |
|------|------|------|
| **文件系统存路径（本方案）** | 读取快、备份简单、节省数据库空间 | 需管理文件与记录的一致性 |
| **MySQL BLOB 直接存储** | 数据一体化、易于迁移 | 数据库膨胀、备份慢、影响查询性能 |

**选择存路径的原因**：
1. 大文件会显著降低数据库查询性能
2. 数据库存储成本远高于文件存储
3. 备份恢复更灵活（元数据与文件分开）
4. 图片可通过 Web 服务器直接访问，无需经过后端
5. 未来可平滑迁移至 OSS 对象存储

markdown
# FaceShield 数据库设计文档



## 一、设计概述

### 1.1 设计目标

- 完整存储用户上传的截屏图片元数据
- 追踪每次检测任务的执行状态
- 存储频域-空域融合模型的完整检测结果
- 支持历史记录查询与统计分析
- 保障用户数据隔离与安全性

### 1.2 设计原则

1. **第三范式（3NF）** ：消除数据冗余，字段依赖主键
2. **外键关联**：通过外键建立表间关系，保证数据一致性
3. **索引优化**：对高频查询字段建立索引，提升查询性能
4. **数据隔离**：所有查询带 `user_id` 条件，防止越权访问
5. **可扩展性**：预留字段支持未来功能扩展


## 二、表结构总览

| 表名 | 说明 | 记录数（演示） |
|------|------|---------------|
| users | 用户账户信息 | 1 |
| file_record | 上传文件记录 | 2 |
| detection_task | 检测任务状态 | 2 |
| detection_result | 检测结果详情 | 2 |
| model_version | 模型版本管理 | 1 |
| detection_records（视图） | 检测记录联表查询 | 2 |


## 三、关系说明

### 3.1 外键依赖链
users.id
↓
file_record.user_id (一个用户上传多个文件)
↓
detection_task.file_id (一个文件对应多个检测任务)
↓
detection_result.task_id (一个任务对应一个检测结果)

text

### 3.2 删除策略

| 操作 | 策略 |
|------|------|
| 删除用户 | 软删除（status='disabled'）或级联删除关联数据 |
| 删除文件 | `is_deleted` 软删除标记，不物理删除文件记录 |
| 删除检测任务 | 保留结果，仅标记任务状态为 failed |


## 四、索引策略

| 表名 | 索引字段 | 用途 |
|------|---------|------|
| users | username | 加速登录查询 |
| file_record | user_id | 加速按用户查询文件 |
| file_record | image_hash | 加速去重校验 |
| file_record | stored_filename | 保证唯一性 |
| detection_task | user_id | 加速按用户查询任务 |
| detection_task | file_id | 加速按文件查询任务 |
| detection_task | task_status | 加速按状态筛选任务 |
| detection_result | user_id | 加速按用户查询结果 |
| detection_result | task_id | 加速按任务查询结果 |
| detection_result | created_at | 加速按时间排序查询 |
| model_version | model_name, version | 加速按名称/版本查询 |


## 五、存储策略

| 数据类型 | 存储方式 | 存储位置 | 数据库存储内容 |
|---------|---------|---------|---------------|
| 用户上传图片 | 文件系统 | `/uploads/images/{YYYY-MM-DD}/` | 文件路径 + 哈希值 |
| 裁剪人脸图 | 文件系统 | `/uploads/crops/{YYYY-MM-DD}/` | URL |
| Grad-CAM热力图 | 文件系统 | `/uploads/heatmaps/{YYYY-MM-DD}/` | URL |
| 模型权重文件 | 文件系统 | `/models/{version}/` | 文件路径 |
| 用户信息 | 数据库 | MySQL | 完整记录 |
| 检测结果 | 数据库 | MySQL | 完整记录 |


## 六、备份与恢复

### 6.1 备份策略

| 策略 | 说明 |
|------|------|
| 备份频率 | 每日凌晨2:00自动备份 |
| 保留周期 | 保留最近7天备份 |
| 备份内容 | 完整数据库（含表结构 + 数据） |
| 备份工具 | mysqldump |

### 6.2 备份命令

```bash
mysqldump -u faceshield_user -p faceshield_db > backup_$(date +%Y%m%d).sql
6.3 恢复命令
bash
mysql -u faceshield_user -p faceshield_db < backup_20260708.sql
七、安全设计
安全措施	说明
密码加密	password_hash 使用 bcrypt 加密
数据隔离	所有查询必须带 user_id 条件
非 root 账号	应用使用 faceshield_user 连接
配置文件	.env 存放密码，不提交 GitHub
HTTPS 传输	图片上传使用 HTTPS 加密
