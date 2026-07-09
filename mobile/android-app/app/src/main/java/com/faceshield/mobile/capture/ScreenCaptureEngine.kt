package com.faceshield.mobile.capture

import android.content.Context
import android.graphics.Bitmap
import android.media.Image
import android.media.ImageReader
import com.faceshield.mobile.model.CaptureResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream

class ScreenCaptureEngine(
    private val context: Context,
    private val mediaProjectionManager: MediaProjectionManager
) {

    suspend fun captureScreen(maxEdge: Int = 1440, quality: Int = 90): CaptureResult =
        withContext(Dispatchers.IO) {
            if (!mediaProjectionManager.isAuthorized.value) {
                return@withContext CaptureResult.NotAuthorized
            }

            val metrics = context.resources.displayMetrics
            try {
                val imageReader = mediaProjectionManager.createVirtualDisplay(
                    metrics.widthPixels,
                    metrics.heightPixels
                ) ?: return@withContext CaptureResult.ProjectionSessionLost

                val image = acquireLatestImageWithRetry(imageReader)
                    ?: return@withContext CaptureResult.EmptyFrame

                val bitmap = try {
                    imageToBitmap(image)
                } finally {
                    image.close()
                }

                if (bitmap == null) {
                    return@withContext CaptureResult.EmptyFrame
                }

                val resized = resizeIfNeeded(bitmap, maxEdge)
                val file = compressAndSave(resized, quality)

                if (bitmap != resized) bitmap.recycle()
                resized.recycle()

                if (file == null) CaptureResult.EmptyFrame else CaptureResult.Success(file)
            } catch (e: SecurityException) {
                mediaProjectionManager.releaseVirtualDisplay()
                CaptureResult.BlockedBySystem
            } catch (e: Exception) {
                val msg = e.message.orEmpty()
                if (
                    msg.contains("FLAG_SECURE", ignoreCase = true) ||
                    msg.contains("DRM", ignoreCase = true)
                ) {
                    CaptureResult.BlockedBySystem
                } else {
                    CaptureResult.EmptyFrame
                }
            }
            // 不释放 VirtualDisplay —— 保持活跃可防止系统回收 MediaProjection，
            // 下次截屏时 createVirtualDisplay 会自动释放旧的再创建新的
        }

    private suspend fun acquireLatestImageWithRetry(
        imageReader: ImageReader,
        attempts: Int = 5,
        delayMs: Long = 80
    ): Image? {
        repeat(attempts) {
            delay(delayMs)
            val image = imageReader.acquireLatestImage()
            if (image != null) return image
        }
        return null
    }

    private fun imageToBitmap(image: Image): Bitmap? {
        val plane = image.planes.firstOrNull() ?: return null
        val buffer = plane.buffer
        val pixelStride = plane.pixelStride
        val rowStride = plane.rowStride
        val rowPadding = rowStride - pixelStride * image.width

        val paddedBitmap = Bitmap.createBitmap(
            image.width + rowPadding / pixelStride,
            image.height,
            Bitmap.Config.ARGB_8888
        )
        paddedBitmap.copyPixelsFromBuffer(buffer)

        return if (paddedBitmap.width == image.width) {
            paddedBitmap
        } else {
            val cropped = Bitmap.createBitmap(paddedBitmap, 0, 0, image.width, image.height)
            paddedBitmap.recycle()
            cropped
        }
    }

    private fun resizeIfNeeded(bitmap: Bitmap, maxEdge: Int): Bitmap {
        val maxDimension = maxOf(bitmap.width, bitmap.height)
        if (maxDimension <= maxEdge) return bitmap

        val scale = maxEdge.toFloat() / maxDimension.toFloat()
        val newWidth = (bitmap.width * scale).toInt().coerceAtLeast(1)
        val newHeight = (bitmap.height * scale).toInt().coerceAtLeast(1)
        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }

    private fun compressAndSave(bitmap: Bitmap, quality: Int): File? {
        val file = File(context.cacheDir, "mobile_capture_${System.currentTimeMillis()}.jpg")
        var currentQuality = quality.coerceIn(50, 100)
        var outputStream: ByteArrayOutputStream

        do {
            outputStream = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, currentQuality, outputStream)
            if (outputStream.size() <= 2 * 1024 * 1024) break
            currentQuality -= 5
        } while (currentQuality >= 50)

        FileOutputStream(file).use { it.write(outputStream.toByteArray()) }
        return if (file.exists() && file.length() > 0) file else null
    }
}
