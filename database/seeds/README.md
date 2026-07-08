-- ============================================================
-- FaceShield 演示测试数据
-- 说明：支持重复执行不报错
-- ============================================================

USE faceshield_db;

-- 清理旧测试数据（可选）
SET @demo_user_id = (SELECT id FROM users WHERE username = 'demo_user');

-- 如果已有测试数据，先清理（按外键依赖顺序删除）
DELETE FROM detection_result WHERE user_id = @demo_user_id;
DELETE FROM detection_task WHERE user_id = @demo_user_id;
DELETE FROM file_record WHERE user_id = @demo_user_id;

-- ============================================================
-- 测试数据1：真实图片检测
-- ============================================================

-- 插入文件记录
INSERT INTO file_record (
    user_id, original_filename, stored_filename, image_hash, file_path, file_size
)
SELECT
    @demo_user_id,
    'real_face_01.jpg',
    'real_face_01_abc123.jpg',
    'a1b2c3d4e5f67890abcdef1234567890',
    '/uploads/images/2026-07-08/real_face_01_abc123.jpg',
    204800
WHERE NOT EXISTS (
    SELECT 1 FROM file_record 
    WHERE stored_filename = 'real_face_01_abc123.jpg'
);

-- 插入检测任务
INSERT INTO detection_task (
    user_id, file_id, task_status, task_type, started_at, finished_at
)
SELECT
    @demo_user_id,
    (SELECT id FROM file_record WHERE stored_filename = 'real_face_01_abc123.jpg'),
    'completed',
    'image',
    NOW() - INTERVAL 5 MINUTE,
    NOW() - INTERVAL 4 MINUTE
WHERE NOT EXISTS (
    SELECT 1 FROM detection_task 
    WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'real_face_01_abc123.jpg')
);

-- 插入检测结果
INSERT INTO detection_result (
    user_id, task_id, file_id, label, fake_probability, confidence,
    risk_level, frequency_score, spatial_score, model_version, face_detected,
    face_crop_url, heatmap_url, suggestion
)
SELECT
    @demo_user_id,
    (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'real_face_01_abc123.jpg')),
    (SELECT id FROM file_record WHERE stored_filename = 'real_face_01_abc123.jpg'),
    'real',
    0.0800, 0.9200,
    'low',
    0.9500, 0.8900,
    'v0.1',
    TRUE,
    '/uploads/crops/2026-07-08/real_crop.jpg',
    '/uploads/heatmaps/2026-07-08/real_heatmap.jpg',
    '该图片经检测为真实人脸，未发现明显伪造痕迹。'
WHERE NOT EXISTS (
    SELECT 1 FROM detection_result 
    WHERE task_id = (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'real_face_01_abc123.jpg'))
);

-- ============================================================
-- 测试数据2：伪造图片检测（高风险）
-- ============================================================

INSERT INTO file_record (
    user_id, original_filename, stored_filename, image_hash, file_path, file_size
)
SELECT
    @demo_user_id,
    'fake_face_01.jpg',
    'fake_face_01_xyz789.jpg',
    'f6e5d4c3b2a19087fedcba0987654321',
    '/uploads/images/2026-07-08/fake_face_01_xyz789.jpg',
    153600
WHERE NOT EXISTS (
    SELECT 1 FROM file_record 
    WHERE stored_filename = 'fake_face_01_xyz789.jpg'
);

INSERT INTO detection_task (
    user_id, file_id, task_status, task_type, started_at, finished_at
)
SELECT
    @demo_user_id,
    (SELECT id FROM file_record WHERE stored_filename = 'fake_face_01_xyz789.jpg'),
    'completed',
    'image',
    NOW() - INTERVAL 3 MINUTE,
    NOW() - INTERVAL 2 MINUTE
WHERE NOT EXISTS (
    SELECT 1 FROM detection_task 
    WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_01_xyz789.jpg')
);

INSERT INTO detection_result (
    user_id, task_id, file_id, label, fake_probability, confidence,
    risk_level, frequency_score, spatial_score, model_version, face_detected,
    face_crop_url, heatmap_url, suggestion
)
SELECT
    @demo_user_id,
    (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_01_xyz789.jpg')),
    (SELECT id FROM file_record WHERE stored_filename = 'fake_face_01_xyz789.jpg'),
    'fake',
    0.8760, 0.9400,
    'high',
    0.8500, 0.9100,
    'v0.1',
    TRUE,
    '/uploads/crops/2026-07-08/fake_crop.jpg',
    '/uploads/heatmaps/2026-07-08/fake_heatmap.jpg',
    '该图片经检测为深度伪造人脸，建议进一步核实对方身份。'
WHERE NOT EXISTS (
    SELECT 1 FROM detection_result 
    WHERE task_id = (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_01_xyz789.jpg'))
);

-- ============================================================
-- 测试数据3：伪造图片检测（中风险）
-- ============================================================

INSERT INTO file_record (
    user_id, original_filename, stored_filename, image_hash, file_path, file_size
)
SELECT
    @demo_user_id,
    'fake_face_02.jpg',
    'fake_face_02_def456.jpg',
    '1234567890abcdef1234567890abcdef',
    '/uploads/images/2026-07-08/fake_face_02_def456.jpg',
    102400
WHERE NOT EXISTS (
    SELECT 1 FROM file_record 
    WHERE stored_filename = 'fake_face_02_def456.jpg'
);

INSERT INTO detection_task (
    user_id, file_id, task_status, task_type, started_at, finished_at
)
SELECT
    @demo_user_id,
    (SELECT id FROM file_record WHERE stored_filename = 'fake_face_02_def456.jpg'),
    'completed',
    'image',
    NOW() - INTERVAL 1 MINUTE,
    NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM detection_task 
    WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_02_def456.jpg')
);

INSERT INTO detection_result (
    user_id, task_id, file_id, label, fake_probability, confidence,
    risk_level, frequency_score, spatial_score, model_version, face_detected,
    face_crop_url, heatmap_url, suggestion
)
SELECT
    @demo_user_id,
    (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_02_def456.jpg')),
    (SELECT id FROM file_record WHERE stored_filename = 'fake_face_02_def456.jpg'),
    'fake',
    0.6500, 0.7800,
    'medium',
    0.6700, 0.6200,
    'v0.1',
    TRUE,
    '/uploads/crops/2026-07-08/fake_crop_02.jpg',
    '/uploads/heatmaps/2026-07-08/fake_heatmap_02.jpg',
    '该图片存在部分伪造迹象，建议结合更多信息综合判断。'
WHERE NOT EXISTS (
    SELECT 1 FROM detection_result 
    WHERE task_id = (SELECT id FROM detection_task WHERE file_id = (SELECT id FROM file_record WHERE stored_filename = 'fake_face_02_def456.jpg'))
);

-- ============================================================
-- 验证数据
-- ============================================================
SELECT '======= 检测记录视图验证 =======' AS '';
SELECT * FROM detection_records WHERE user_id = @demo_user_id ORDER BY created_at DESC;

SELECT '======= 统计概览 =======' AS '';
SELECT 
    COUNT(*) AS total_detections,
    SUM(CASE WHEN prediction = 'fake' THEN 1 ELSE 0 END) AS fake_count,
    SUM(CASE WHEN prediction = 'real' THEN 1 ELSE 0 END) AS real_count,
    ROUND(AVG(fake_probability), 4) AS avg_fake_prob
FROM detection_records 
WHERE user_id = @demo_user_id;
