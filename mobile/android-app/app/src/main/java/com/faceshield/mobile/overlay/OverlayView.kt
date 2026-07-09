package com.faceshield.mobile.overlay

import android.annotation.SuppressLint
import android.app.Dialog
import android.content.Context
import android.graphics.PixelFormat
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import com.faceshield.mobile.model.OverlayState
import kotlin.math.abs
import kotlin.math.roundToInt
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class OverlayView(
    private val context: Context,
    private val stateFlow: StateFlow<OverlayState>,
    private val onClick: () -> Unit,
    private val onLongClick: () -> Unit
) {

    companion object {
        private const val TAG = "FaceShieldOverlayView"
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var collectJob: Job? = null

    private var dialog: Dialog? = null
    private var statusIndicator: View? = null
    private var lastState: OverlayState = OverlayState.IDLE

    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f
    private var isDragging = false
    private var downTime = 0L

    private val density = context.resources.displayMetrics.density
    private val indicatorSize = (56 * density).roundToInt()

    fun show(): Boolean {
        if (dialog?.isShowing == true) return true

        val dlg = Dialog(context, android.R.style.Theme_Translucent_NoTitleBar).apply {
            setCancelable(false)
            setCanceledOnTouchOutside(false)
            window?.apply {
                setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
                addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
                setLayout(500, 300)
                setGravity(Gravity.TOP or Gravity.START)
                attributes.x = 100
                attributes.y = 200
                setBackgroundDrawableResource(android.R.color.transparent)
                setFormat(PixelFormat.TRANSLUCENT)
            }
        }

        dlg.setContentView(createOverlayView())

        dialog = dlg
        dlg.show()

        // 检查对话框是否真的显示出来了
        if (!dlg.isShowing) {
            dialog = null
            return false
        }

        collectJob = scope.launch {
            stateFlow.collect { state -> updateState(state) }
        }
        return true
    }

    fun hide() {
        dialog?.dismiss()
        dialog = null
        statusIndicator = null
        collectJob?.cancel()
        collectJob = null
    }

    @SuppressLint("ClickableViewAccessibility")
    private fun createOverlayView(): View {
        val view = FrameLayout(context).apply {
            layoutParams = FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )

            val indicator = View(context).also { v ->
                statusIndicator = v
                v.layoutParams = FrameLayout.LayoutParams(indicatorSize, indicatorSize).apply {
                    gravity = Gravity.CENTER
                }
                val shape = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL
                    setColor(0xFF1565C0.toInt())
                    setStroke((1.5f * density).roundToInt(), 0xAAFFFFFF.toInt())
                }
                v.background = shape
            }

            val bg = GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                cornerRadii = floatArrayOf(16f, 16f, 16f, 16f, 16f, 16f, 16f, 16f)
                setColor(0xDD1A1A2E.toInt())
            }
            background = bg

            setPadding(8, 8, 8, 8)
            addView(indicator)
        }

        view.setOnTouchListener { _, event -> handleTouchEvent(event) }
        view.setOnLongClickListener {
            onLongClick()
            true
        }
        return view
    }

    private fun handleTouchEvent(event: MotionEvent): Boolean {
        val lp = dialog?.window?.attributes ?: return false

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                initialX = lp.x
                initialY = lp.y
                initialTouchX = event.rawX
                initialTouchY = event.rawY
                isDragging = false
                downTime = System.currentTimeMillis()
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.rawX - initialTouchX
                val dy = event.rawY - initialTouchY
                val touchSlop = (10 * density).toInt()
                if (!isDragging && (abs(dx) > touchSlop || abs(dy) > touchSlop)) {
                    isDragging = true
                }
                if (isDragging) {
                    lp.x = initialX + dx.toInt()
                    lp.y = initialY + dy.toInt()
                    dialog?.window?.attributes = lp
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
        val lp = dialog?.window?.attributes ?: return
        val metrics = context.resources.displayMetrics
        val buttonWidth = indicatorSize + (12 * density).roundToInt()
        val centerX = lp.x + buttonWidth / 2
        lp.x = if (centerX < metrics.widthPixels / 2) 0 else metrics.widthPixels - buttonWidth
        dialog?.window?.attributes = lp
    }

    private fun updateState(state: OverlayState) {
        lastState = state
        val color = getColorForState(state)
        statusIndicator?.let {
            val shape = GradientDrawable().apply {
                shape = GradientDrawable.OVAL
                setColor(color)
                setStroke((1.5f * density).roundToInt(), 0xAAFFFFFF.toInt())
            }
            it.background = shape
        }
    }

    private fun getColorForState(state: OverlayState): Int {
        return when (state) {
            OverlayState.IDLE -> 0xFF1565C0.toInt()
            OverlayState.PERMISSION_REQUIRED -> 0xFF9E9E9E.toInt()
            OverlayState.CAPTURING,
            OverlayState.UPLOADING,
            OverlayState.DETECTING -> 0xFF1565C0.toInt()
            OverlayState.SUCCESS_LOW -> 0xFF00E676.toInt()
            OverlayState.SUCCESS_MEDIUM -> 0xFFFF9100.toInt()
            OverlayState.SUCCESS_HIGH -> 0xFFF44336.toInt()
            OverlayState.FAILURE -> 0xFF9E9E9E.toInt()
        }
    }

}
