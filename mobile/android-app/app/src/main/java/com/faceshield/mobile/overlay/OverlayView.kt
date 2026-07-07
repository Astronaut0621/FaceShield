package com.faceshield.mobile.overlay

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.PixelFormat
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import com.faceshield.mobile.model.OverlayState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlin.math.abs

class OverlayView(
    private val context: Context,
    private val stateFlow: StateFlow<OverlayState>,
    private val onClick: () -> Unit,
    private val onLongClick: () -> Unit
) {

    private val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var collectJob: Job? = null

    private var overlayView: View? = null
    private var statusIndicator: View? = null
    private var stateLabel: TextView? = null

    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    private var isDragging = false
    private var downTime = 0L

    private val layoutParams = WindowManager.LayoutParams().apply {
        width = WindowManager.LayoutParams.WRAP_CONTENT
        height = WindowManager.LayoutParams.WRAP_CONTENT
        type = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
            WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS
        format = PixelFormat.TRANSLUCENT
        gravity = Gravity.TOP or Gravity.START
        x = 0
        y = 300
    }

    fun show(): Boolean {
        if (overlayView != null) return true

        val nextView = createOverlayView()
        val added = runCatching {
            windowManager.addView(nextView, layoutParams)
        }.isSuccess

        if (!added) {
            overlayView = null
            statusIndicator = null
            stateLabel = null
            return false
        }

        overlayView = nextView

        collectJob = scope.launch {
            stateFlow.collect { state -> updateState(state) }
        }
        return true
    }

    fun hide() {
        overlayView?.let { view ->
            runCatching { windowManager.removeView(view) }
        }
        overlayView = null
        statusIndicator = null
        stateLabel = null
        collectJob?.cancel()
        collectJob = null
    }

    @SuppressLint("ClickableViewAccessibility")
    private fun createOverlayView(): View {
        val density = context.resources.displayMetrics.density
        val sizePx = (52 * density).toInt()

        val container = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(4, 4, 4, 4)
        }

        statusIndicator = ImageView(context).apply {
            layoutParams = LinearLayout.LayoutParams(sizePx, sizePx)
            setBackgroundColor(getColorForState(OverlayState.IDLE))
        }

        stateLabel = TextView(context).apply {
            textSize = 9f
            setTextColor(android.graphics.Color.WHITE)
            text = "FS"
            setPadding(4, 2, 4, 2)
            setBackgroundColor(0x99000000.toInt())
        }

        container.addView(statusIndicator)
        container.addView(stateLabel)
        container.setOnTouchListener { _, event -> handleTouchEvent(event) }
        return container
    }

    private fun handleTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                initialX = layoutParams.x
                initialY = layoutParams.y
                initialTouchX = event.rawX
                initialTouchY = event.rawY
                isDragging = false
                downTime = System.currentTimeMillis()
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.rawX - initialTouchX
                val dy = event.rawY - initialTouchY
                val touchSlop = (10 * context.resources.displayMetrics.density).toInt()
                if (!isDragging && (abs(dx) > touchSlop || abs(dy) > touchSlop)) {
                    isDragging = true
                }
                if (isDragging) {
                    layoutParams.x = initialX + dx.toInt()
                    layoutParams.y = initialY + dy.toInt()
                    overlayView?.let { view ->
                        runCatching { windowManager.updateViewLayout(view, layoutParams) }
                    }
                }
                return true
            }

            MotionEvent.ACTION_UP -> {
                if (isDragging) {
                    snapToEdge()
                } else if (System.currentTimeMillis() - downTime > 500) {
                    onLongClick()
                } else {
                    onClick()
                }
                return true
            }
        }
        return false
    }

    private fun snapToEdge() {
        val metrics = context.resources.displayMetrics
        val buttonWidth = (52 * metrics.density).toInt()
        val centerX = layoutParams.x + buttonWidth / 2
        layoutParams.x = if (centerX < metrics.widthPixels / 2) {
            0
        } else {
            metrics.widthPixels - buttonWidth
        }
        overlayView?.let { view ->
            runCatching { windowManager.updateViewLayout(view, layoutParams) }
        }
    }

    private fun updateState(state: OverlayState) {
        statusIndicator?.setBackgroundColor(getColorForState(state))
        stateLabel?.text = getLabelForState(state)
    }

    private fun getColorForState(state: OverlayState): Int {
        return when (state) {
            OverlayState.IDLE -> 0xFF1565C0.toInt()
            OverlayState.PERMISSION_REQUIRED -> 0xFF9E9E9E.toInt()
            OverlayState.CAPTURING,
            OverlayState.UPLOADING,
            OverlayState.DETECTING -> 0xFF1565C0.toInt()
            OverlayState.SUCCESS_LOW -> 0xFF4CAF50.toInt()
            OverlayState.SUCCESS_MEDIUM -> 0xFFFF9800.toInt()
            OverlayState.SUCCESS_HIGH -> 0xFFF44336.toInt()
            OverlayState.FAILURE -> 0xFF9E9E9E.toInt()
        }
    }

    private fun getLabelForState(state: OverlayState): String {
        return when (state) {
            OverlayState.IDLE -> "FS"
            OverlayState.PERMISSION_REQUIRED -> "AUTH"
            OverlayState.CAPTURING -> "CAP"
            OverlayState.UPLOADING -> "UP"
            OverlayState.DETECTING -> "AI"
            OverlayState.SUCCESS_LOW -> "LOW"
            OverlayState.SUCCESS_MEDIUM -> "MED"
            OverlayState.SUCCESS_HIGH -> "HIGH"
            OverlayState.FAILURE -> "ERR"
        }
    }
}
