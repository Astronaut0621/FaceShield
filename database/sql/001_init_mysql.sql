CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP NULL,
    INDEX ix_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS file_record (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    image_hash VARCHAR(128),
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX ix_file_record_user_id (user_id),
    INDEX ix_file_record_image_hash (image_hash),
    CONSTRAINT fk_file_record_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS detection_task (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    file_id INT NOT NULL,
    task_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    task_type VARCHAR(50) NOT NULL DEFAULT 'image',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    INDEX ix_detection_task_user_id (user_id),
    INDEX ix_detection_task_file_id (file_id),
    CONSTRAINT fk_detection_task_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),
    CONSTRAINT fk_detection_task_file
        FOREIGN KEY (file_id)
        REFERENCES file_record(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS detection_result (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    task_id INT NOT NULL,
    file_id INT NOT NULL,
    label VARCHAR(50),
    fake_probability DECIMAL(6, 4),
    confidence DECIMAL(6, 4),
    risk_level VARCHAR(50),
    frequency_score DECIMAL(6, 4),
    spatial_score DECIMAL(6, 4),
    heatmap_url VARCHAR(500),
    face_crop_url VARCHAR(500),
    face_detected BOOLEAN NOT NULL DEFAULT FALSE,
    suggestion TEXT,
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX ix_detection_result_user_id (user_id),
    INDEX ix_detection_result_task_id (task_id),
    INDEX ix_detection_result_file_id (file_id),
    CONSTRAINT fk_detection_result_user
        FOREIGN KEY (user_id)
        REFERENCES users(id),
    CONSTRAINT fk_detection_result_task
        FOREIGN KEY (task_id)
        REFERENCES detection_task(id),
    CONSTRAINT fk_detection_result_file
        FOREIGN KEY (file_id)
        REFERENCES file_record(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS model_version (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    model_path VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_model_version_name_version (model_name, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
