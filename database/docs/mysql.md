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
