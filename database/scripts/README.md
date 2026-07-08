-- ============================================================
-- FaceShield 常用查询示例
-- ============================================================

USE faceshield_db;

-- 1. 查询所有历史检测记录（按时间倒序）
SELECT * FROM detection_records ORDER BY created_at DESC;

-- 2. 只查看伪造记录
SELECT * FROM detection_records WHERE prediction = 'fake' ORDER BY created_at DESC;

-- 3. 只查看真实记录
SELECT * FROM detection_records WHERE prediction = 'real' ORDER BY created_at DESC;

-- 4. 按风险等级筛选
SELECT * FROM detection_records WHERE risk_level = 'high' ORDER BY created_at DESC;

-- 5. 查询最近7天的检测记录
SELECT * FROM detection_records
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY created_at DESC;

-- 6. 统计概览
SELECT
    COUNT(*) AS total_detections,
    SUM(CASE WHEN prediction = 'fake' THEN 1 ELSE 0 END) AS fake_count,
    SUM(CASE WHEN prediction = 'real' THEN 1 ELSE 0 END) AS real_count,
    ROUND(AVG(fake_probability), 4) AS avg_fake_prob,
    ROUND(SUM(CASE WHEN prediction = 'fake' THEN fake_probability ELSE 0 END) /
          NULLIF(SUM(CASE WHEN prediction = 'fake' THEN 1 ELSE 0 END), 0), 4) AS avg_fake_prob_fake_only
FROM detection_records;

-- 7. 按日统计检测量趋势
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS daily_total,
    SUM(CASE WHEN prediction = 'fake' THEN 1 ELSE 0 END) AS daily_fake,
    SUM(CASE WHEN prediction = 'real' THEN 1 ELSE 0 END) AS daily_real
FROM detection_records
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 8. 查看当前激活的模型版本
SELECT * FROM model_version WHERE is_active = TRUE;


@echo off
:: ============================================================
:: FaceShield 数据库备份脚本（Windows）
:: 每日定时备份，保留最近7天
:: 使用方法：双击运行 或 添加到计划任务
:: ============================================================

set DB_HOST=localhost
set DB_PORT=3306
set DB_NAME=faceshield_db
set DB_USER=faceshield_user
set DB_PASS=Faceshield@2026
set BACKUP_DIR=D:\backups\mysql
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%

:: 创建备份目录（如不存在）
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

:: 执行备份
echo 正在备份数据库 %DB_NAME% ...
"D:\MySQL\bin\mysqldump" -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASS% %DB_NAME% > "%BACKUP_DIR%\faceshield_db_%DATE%.sql"

:: 检查是否成功
if %errorlevel% == 0 (
    echo 备份成功：%BACKUP_DIR%\faceshield_db_%DATE%.sql
) else (
    echo 备份失败，请检查数据库连接和密码。
    pause
    exit /b 1
)

:: 删除7天前的备份
forfiles /p "%BACKUP_DIR%" /m "faceshield_db_*.sql" /d -7 /c "cmd /c del /f @path" 2>nul

echo 备份完成，已保留最近7天的备份。
pause
