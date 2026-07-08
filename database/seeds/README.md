-- ============================================================
-- FaceShield 演示测试数据
-- 日期：2026-07-08
-- 说明：插入完整的检测记录链路，覆盖 fake 和 real 两种结果
-- ============================================================

USE faceshield_db;

-- 1. 确保演示用户存在
INSERT INTO users (username, password_hash, display_name, status)
SELECT 'demo_user', 'hashed_demo_password', '演示用户', 'active'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'demo_user');

-- 2. 文件记录（2条：1张伪造图，1张真实图）
INSERT INTO file_record (user_id, original_filename, stored_filename, image_hash, file_path, file_size)
VALUES
    (1, 'fake_face.jpg', 'fake_abc123.jpg', 'a1b2c3d4e5f6789012345678', '/uploads/images/2026-07-08/fake_face.jpg', 204800),
    (1, 'real_face.jpg', 'real_def456.jpg', 'f6e5d4c3b2a1908712345678', '/uploads/images/2026-07-08/real_face.jpg', 184320);

-- 3. 检测任务（2条）
INSERT INTO detection_task (user_id, file_id, task_status, task_type, started_at, finished_at)
VALUES
    (1, 1, 'completed', 'image', NOW(), NOW()),
    (1, 2, 'completed', 'image', NOW(), NOW());

-- 4. 检测结果（2条）
INSERT INTO detection_result (
    user_id, task_id, file_id, label, fake_probability, confidence,
    risk_level, frequency_score, spatial_score,
    heatmap_url, face_crop_url, face_detected, suggestion, model_version
) VALUES
    (1, 1, 1, 'fake', 0.8760, 0.9200, 'high', 0.8900, 0.9500,
     '/uploads/heatmaps/2026-07-08/fake_heatmap.jpg', '/uploads/crops/2026-07-08/fake_crop.jpg', TRUE,
     '检测到伪造特征，建议立即挂断视频通话并核实对方身份。', 'v0.1'),
    (1, 2, 2, 'real', 0.0430, 0.9570, 'low', 0.0600, 0.0300,
     '/uploads/heatmaps/2026-07-08/real_heatmap.jpg', '/uploads/crops/2026-07-08/real_crop.jpg', TRUE,
     '该图片为真实人脸，未检测到明显的伪造痕迹。', 'v0.1');

-- 5. 验证视图查询
SELECT * FROM detection_records;
