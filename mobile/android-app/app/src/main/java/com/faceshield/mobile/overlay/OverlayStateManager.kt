package com.faceshield.mobile.overlay

import com.faceshield.mobile.model.OverlayState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class OverlayStateManager(
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Main)
) {

    private val _state = MutableStateFlow(OverlayState.IDLE)
    val state: StateFlow<OverlayState> = _state.asStateFlow()
    private var resetJob: Job? = null

    fun transitionTo(newState: OverlayState) {
        resetJob?.cancel()
        _state.value = newState
    }

    fun resetAfterDelay(delayMs: Long = 3000) {
        resetJob?.cancel()
        resetJob = scope.launch {
            delay(delayMs)
            _state.value = OverlayState.IDLE
        }
    }
}
