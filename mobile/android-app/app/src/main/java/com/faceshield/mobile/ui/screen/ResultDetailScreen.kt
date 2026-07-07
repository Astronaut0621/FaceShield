package com.faceshield.mobile.ui.screen

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.faceshield.mobile.FaceShieldApp
import com.faceshield.mobile.detection.DetectionRepository
import com.faceshield.mobile.model.DetectionResult
import com.faceshield.mobile.model.NetworkResult
import com.faceshield.mobile.model.RiskLevel
import com.faceshield.mobile.network.ServerUrl
import kotlinx.coroutines.flow.firstOrNull

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultDetailScreen(taskId: Int, onBack: () -> Unit) {
    val context = LocalContext.current
    var result by remember { mutableStateOf<DetectionResult?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(taskId) {
        val app = context.applicationContext as FaceShieldApp
        val serverUrl = app.authTokenStore.serverUrl.firstOrNull().orEmpty()
        if (serverUrl.isBlank()) {
            errorMessage = "Backend URL is not configured."
            isLoading = false
            return@LaunchedEffect
        }
        val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
        if (normalizedServerUrl == null) {
            errorMessage = "Backend URL is invalid. Update it in Settings."
            isLoading = false
            return@LaunchedEffect
        }

        when (val response = DetectionRepository(app.getApi(normalizedServerUrl)).getRecordDetail(taskId)) {
            is NetworkResult.Success -> result = response.data
            is NetworkResult.Error -> errorMessage = response.message
            is NetworkResult.Exception -> errorMessage = "Network error."
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Detection Result") },
                navigationIcon = {
                    TextButton(onClick = onBack) { Text("Back") }
                }
            )
        }
    ) { padding ->
        when {
            isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            errorMessage != null -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    Text(errorMessage.orEmpty(), color = MaterialTheme.colorScheme.error)
                }
            }
            result != null -> result?.let { ResultContent(it, Modifier.padding(padding)) }
        }
    }
}

@Composable
private fun ResultContent(result: DetectionResult, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Detection #${result.taskId}", style = MaterialTheme.typography.titleLarge)

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Risk level", style = MaterialTheme.typography.labelMedium)
                Text(
                    text = result.riskLevel.displayName,
                    style = MaterialTheme.typography.headlineSmall,
                    color = when (result.riskLevel) {
                        RiskLevel.LOW -> MaterialTheme.colorScheme.primary
                        RiskLevel.MEDIUM -> MaterialTheme.colorScheme.tertiary
                        RiskLevel.HIGH -> MaterialTheme.colorScheme.error
                        RiskLevel.UNKNOWN -> MaterialTheme.colorScheme.onSurfaceVariant
                    }
                )
            }
        }

        DetailRow("Label", result.label)
        result.fakeProbability?.let { DetailRow("Fake probability", "${(it * 100).toInt()}%") }
        result.confidence?.let { DetailRow("Confidence", "${(it * 100).toInt()}%") }
        DetailRow("Face detected", if (result.faceDetected) "Yes" else "No")
        result.frequencyScore?.let { DetailRow("Frequency score", "${(it * 100).toInt()}%") }
        result.spatialScore?.let { DetailRow("Spatial score", "${(it * 100).toInt()}%") }
        result.suggestion?.let { DetailRow("Suggestion", it) }
        result.modelName?.let { DetailRow("Model", it) }
        result.modelVersion?.let { DetailRow("Model version", it) }
        result.createdAt?.let { DetailRow("Detected at", it) }

        if (!result.faceDetected) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)
            ) {
                Text(
                    text = "No clear face was detected. Treat this result as low-confidence.",
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(value, style = MaterialTheme.typography.bodyMedium)
    }
}
