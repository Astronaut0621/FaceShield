package com.faceshield.mobile.ui.theme

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke

/**
 * 品牌标识 — 与 Web 前端一致的「F 标 + FaceShield」组合
 */
@Composable
fun BrandLogo(
    markSize: Int = 42,
    fontSize: Int = 26,
    showTagline: Boolean = false,
    tagline: String = "AI 换脸检测"
) {
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        // F 标：蓝色渐变圆角方块
        Box(
            modifier = Modifier
                .size(markSize.dp)
                .background(
                    brush = Brush.linearGradient(
                        colors = listOf(
                            Color(0xFF93C5FD),
                            Color(0xFF2563EB)
                        ),
                        start = Offset(0f, 0f),
                        end = Offset(Float.POSITIVE_INFINITY, Float.POSITIVE_INFINITY)
                    ),
                    shape = RoundedCornerShape((markSize * 0.32f).dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "F",
                color = Color.White,
                fontWeight = FontWeight.Bold,
                fontSize = (markSize * 0.45f).sp
            )
        }

        Column(modifier = Modifier.padding(start = 10.dp)) {
            Text(
                text = "FaceShield",
                fontWeight = FontWeight.Bold,
                fontSize = fontSize.sp,
                color = if (showTagline) Color.White else Color(0xFF172033)
            )
            if (showTagline) {
                Text(
                    text = tagline,
                    fontSize = 12.sp,
                    color = Color(0xFF94A3B8)
                )
            }
        }
    }
}

/**
 * 人脸识别背景 - 抽象人脸轮廓 + 检测框 + 扫描网格
 * 品牌标识 — 与 Web 前端一致的「F 标 + FaceShield」组合
 * 人脸识别背景 - 抽象人脸轮廓 + 检测框 + 扫描网格
 * 替代原有的可爱装饰，呈现专业 AI 人脸检测风格
 */
@Composable
fun FaceRecognitionBackground(
    modifier: Modifier = Modifier,
    scanColor: Color = DecorativePink,
    gridColor: Color = DecorativeLightPink,
    alpha: Float = 0.15f
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height

        // --- 半透明径向渐变底层（虚化效果） ---
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    scanColor.copy(alpha = 0.12f),
                    scanColor.copy(alpha = 0.04f),
                    Color.Transparent
                ),
                center = Offset(w / 2f, h * 0.4f),
                radius = w * 0.55f
            ),
            radius = w * 0.55f,
            center = Offset(w / 2f, h * 0.4f)
        )

        // --- 抽象人脸轮廓（椭圆） ---
        val faceOval = Path().apply {
            addOval(
                androidx.compose.ui.geometry.Rect(
                    left = w * 0.22f,
                    top = h * 0.15f,
                    right = w * 0.78f,
                    bottom = h * 0.75f
                )
            )
        }
        drawPath(
            faceOval,
            color = gridColor.copy(alpha = alpha * 0.6f),
            style = Stroke(width = 1.5f, cap = StrokeCap.Round)
        )

        // --- 面部特征参考线（眼睛、鼻子位置） ---
        // 左眼
        drawCircle(
            color = gridColor.copy(alpha = alpha * 0.4f),
            radius = 4f,
            center = Offset(w * 0.37f, h * 0.32f)
        )
        // 右眼
        drawCircle(
            color = gridColor.copy(alpha = alpha * 0.4f),
            radius = 4f,
            center = Offset(w * 0.63f, h * 0.32f)
        )
        // 鼻子
        drawCircle(
            color = gridColor.copy(alpha = alpha * 0.25f),
            radius = 3f,
            center = Offset(w * 0.5f, h * 0.45f)
        )

        // --- 人脸检测框（L 形四角标记） ---
        val boxLeft = w * 0.15f
        val boxTop = h * 0.10f
        val boxRight = w * 0.85f
        val boxBottom = h * 0.82f
        val cornerLen = 24f

        // 左上角
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxLeft, boxTop), Offset(boxLeft + cornerLen, boxTop), 2f, StrokeCap.Round)
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxLeft, boxTop), Offset(boxLeft, boxTop + cornerLen), 2f, StrokeCap.Round)
        // 右上角
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxRight, boxTop), Offset(boxRight - cornerLen, boxTop), 2f, StrokeCap.Round)
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxRight, boxTop), Offset(boxRight, boxTop + cornerLen), 2f, StrokeCap.Round)
        // 左下角
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxLeft, boxBottom), Offset(boxLeft + cornerLen, boxBottom), 2f, StrokeCap.Round)
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxLeft, boxBottom), Offset(boxLeft, boxBottom - cornerLen), 2f, StrokeCap.Round)
        // 右下角
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxRight, boxBottom), Offset(boxRight - cornerLen, boxBottom), 2f, StrokeCap.Round)
        drawLine(scanColor.copy(alpha = alpha * 1.5f), Offset(boxRight, boxBottom), Offset(boxRight, boxBottom - cornerLen), 2f, StrokeCap.Round)

        // --- 扫描网格线 ---
        val gridSpacing = w / 6f
        var gx = gridSpacing
        while (gx < w) {
            drawLine(
                gridColor.copy(alpha = alpha * 0.3f),
                Offset(gx, 0f),
                Offset(gx, h),
                0.5f
            )
            gx += gridSpacing
        }
        var gy = gridSpacing
        while (gy < h) {
            drawLine(
                gridColor.copy(alpha = alpha * 0.3f),
                Offset(0f, gy),
                Offset(w, gy),
                0.5f
            )
            gy += gridSpacing
        }
    }
}

/**
 * 顶部波浪装饰（保留但不再被主屏幕使用，可用于其他自定义场景）
 */
@Composable
fun TopWaveDecoration(
    modifier: Modifier = Modifier,
    color: Color = DecorativeLightPink,
    waveHeight: Float = 20f,
    alpha: Float = 0.6f
) {
    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(60.dp)
    ) {
        val waveCount = 6
        val segmentWidth = size.width / waveCount

        val path = Path()
        path.moveTo(0f, size.height)

        for (i in 0..waveCount) {
            val x = i * segmentWidth
            val controlX1 = x + segmentWidth * 0.25f
            val controlX2 = x + segmentWidth * 0.75f
            val nextX = x + segmentWidth
            val y = if (i % 2 == 0) size.height - waveHeight else size.height
            path.cubicTo(controlX1, size.height - waveHeight, controlX2, size.height, nextX, y)
        }

        path.lineTo(size.width, size.height)
        path.close()

        drawPath(path, color = color.copy(alpha = alpha))
    }
}

/**
 * 底部波浪装饰线（保留但不再被主屏幕使用）
 */
@Composable
fun BottomWaveLine(
    modifier: Modifier = Modifier,
    color: Color = DecorativePink,
    strokeWidth: Float = 3f,
    alpha: Float = 0.4f
) {
    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(30.dp)
    ) {
        val waveCount = 4
        val segmentWidth = size.width / waveCount
        val amplitude = size.height / 3

        val path = Path()
        path.moveTo(0f, size.height / 2)

        for (i in 0 until waveCount) {
            val startX = i * segmentWidth
            val midX = startX + segmentWidth / 2
            val endX = startX + segmentWidth
            val controlY = if (i % 2 == 0) size.height / 2 - amplitude else size.height / 2 + amplitude
            path.cubicTo(
                startX + segmentWidth * 0.25f, size.height / 2,
                startX + segmentWidth * 0.75f, controlY,
                midX, controlY
            )
            path.cubicTo(
                midX + segmentWidth * 0.25f, controlY,
                endX - segmentWidth * 0.25f, size.height / 2,
                endX, size.height / 2
            )
        }

        drawPath(
            path,
            color = color.copy(alpha = alpha),
            style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
        )
    }
}

/**
 * 角落装饰（保留但不再被主屏幕使用）
 */
@Composable
fun CornerDecoration(
    modifier: Modifier = Modifier,
    color: Color = DecorativeLightPink,
    alpha: Float = 0.5f
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        val cornerPath = Path().apply {
            moveTo(0f, 40f)
            cubicTo(10f, 30f, 20f, 20f, 40f, 0f)
        }
        drawPath(
            cornerPath,
            color = color.copy(alpha = alpha),
            style = Stroke(width = 2f, cap = StrokeCap.Round)
        )

        val rightPath = Path().apply {
            moveTo(size.width - 40f, 0f)
            cubicTo(size.width - 20f, 20f, size.width - 10f, 30f, size.width, 40f)
        }
        drawPath(
            rightPath,
            color = color.copy(alpha = alpha),
            style = Stroke(width = 2f, cap = StrokeCap.Round)
        )

        drawCircle(
            color = color.copy(alpha = alpha * 0.7f),
            radius = 4f,
            center = Offset(16f, 16f)
        )

        drawCircle(
            color = color.copy(alpha = alpha * 0.7f),
            radius = 4f,
            center = Offset(size.width - 16f, 16f)
        )
    }
}

/**
 * 卡片底部装饰条（保留但不再被主屏幕使用）
 */
@Composable
fun CardBottomStripe(
    modifier: Modifier = Modifier,
    color: Color = DecorativePink,
    alpha: Float = 0.3f
) {
    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(4.dp)
    ) {
        val dashLength = 12f
        val gapLength = 6f
        var x = 0f
        while (x < size.width) {
            val endX = minOf(x + dashLength, size.width)
            drawLine(
                color = color.copy(alpha = alpha),
                start = Offset(x, size.height / 2),
                end = Offset(endX, size.height / 2),
                strokeWidth = size.height,
                cap = StrokeCap.Round
            )
            x += dashLength + gapLength
        }
    }
}
