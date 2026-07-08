-- ============================================================
-- FaceShield 数据库初始化脚本（MySQL版）
-- 数据库：faceshield_db
-- 日期：2026-07-08
-- 说明：支持重复执行不报错
-- ============================================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS faceshield_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE faceshield_db;

-- 2. 创建用户（如已存在则跳过）
CREATE USER IF NOT EXISTS 'faceshield_user'@'localhost' 
IDENTIFIED BY 'Faceshield@2026';

CREATE USER IF NOT EXISTS 'faceshield_user'@'%' 
IDENTIFIED BY 'Faceshield@2026';

-- 3. 授予权限
GRANT ALL PRIVILEGES ON faceshield_db.* TO 'faceshield_user'@'localhost';
GRANT ALL PRIVILEGES ON faceshield_db.* TO 'faceshield_user'@'%';
FLUSH PRIVILEGES;

-- ============================================================
-- 4. 创建核心表
-- ============================================================

-- 4.1 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- 4.2 文件记录表
CREATE TABLE IF NOT EXISTS file_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    image_hash VARCHAR(128),
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_file_record_user
        FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4.3 检测任务表
CREATE TABLE IF NOT EXISTS detection_task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_id INT NOT NULL,
    task_status VARCHAR(50) DEFAULT 'pending',
    task_type VARCHAR(50) DEFAULT 'image',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    CONSTRAINT fk_detection_task_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_detection_task_file
        FOREIGN KEY (file_id) REFERENCES file_record(id)
);

-- 4.4 检测结果表
CREATE TABLE IF NOT EXISTS detection_result (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    task_id INT NOT NULL,
    file_id INT NOT NULL,
    label VARCHAR(50),
    fake_probability DECIMAL(6,4),
    confidence DECIMAL(6,4),
    risk_level VARCHAR(50),
    frequency_score DECIMAL(6,4),
    spatial_score DECIMAL(6,4),
    heatmap_url VARCHAR(500),
    face_crop_url VARCHAR(500),
    face_detected BOOLEAN DEFAULT FALSE,
    suggestion TEXT,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detection_result_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT fk_detection_result_task
        FOREIGN KEY (task_id) REFERENCES detection_task(id),
    CONSTRAINT fk_detection_result_file
        FOREIGN KEY (file_id) REFERENCES file_record(id)
);

-- 4.5 模型版本表
CREATE TABLE IF NOT EXISTS model_version (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    model_path VARCHAR(500),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. 创建检测记录视图
-- ============================================================
CREATE OR REPLACE VIEW detection_records AS
SELECT
    dr.task_id AS id,
    dr.user_id,
    fr.image_hash,
    fr.file_path AS original_image_path,
    dr.face_crop_url AS face_crop_path,
    dr.heatmap_url AS heatmap_path,
    dr.label AS prediction,
    dr.fake_probability,
    dr.risk_level,
    dr.model_version,
    dr.face_detected,
    dr.created_at
FROM detection_result dr
JOIN file_record fr ON fr.id = dr.file_id;

-- ============================================================
-- 6. 插入初始数据
-- ============================================================

-- 6.1 模型版本初始数据
INSERT INTO model_version (
    model_name,
    version,
    description,
    model_path,
    is_active
)
SELECT
    'FaceShield-MockNet',
    'v0.1',
    'Initial mock detection model for frontend/backend integration.',
    NULL,
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM model_version
    WHERE model_name = 'FaceShield-MockNet' AND version = 'v0.1'
);

-- 6.2 演示用户数据（密码：demo123，实际使用需bcrypt加密）
INSERT INTO users (
    username,
    password_hash,
    display_name,
    status,
    created_at
)
SELECT
    'demo_user',
    'hashed_demo_password',
    '演示用户',
    'active',
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'demo_user'
);
