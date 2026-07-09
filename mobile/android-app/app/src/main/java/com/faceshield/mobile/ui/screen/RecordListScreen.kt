package com.faceshield.mobile.ui.screen

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
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
import com.faceshield.mobile.model.DetectionResponse
import com.faceshield.mobile.model.NetworkResult
import com.faceshield.mobile.model.RiskLevel
import com.faceshield.mobile.network.ServerUrl
import kotlinx.coroutines.flow.firstOrNull

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordListScreen(
    onBack: () -> Unit,
    onRecordClick: (taskId: Int) -> Unit
) {
    val context = LocalContext.current
    var records by remember { mutableStateOf<List<DetectionResponse>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        val app = context.applicationContext as FaceShieldApp
        val serverUrl = app.authTokenStore.serverUrl.firstOrNull().orEmpty()
        if (serverUrl.isBlank()) {
            errorMessage = "未配置后端地址"
            isLoading = false
            return@LaunchedEffect
        }
        val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
        if (normalizedServerUrl == null) {
            errorMessage = "后端地址无效，请在设置中更新"
            isLoading = false
            return@LaunchedEffect
        }

        when (val result = DetectionRepository(app.getApi(normalizedServerUrl)).getRecords(1, 50)) {
            is NetworkResult.Success -> records = result.data.items
            is NetworkResult.Error -> errorMessage = result.message
            is NetworkResult.Exception -> errorMessage = "网络错误"
        }
        isLoading = false
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("检测记录") },
                navigationIcon = {
                    TextButton(onClick = onBack) { Text("返回") }
                }
            )
        }
    ) { padding ->
        when {
            isLoading -> CenterBox(padding) { CircularProgressIndicator() }
            errorMessage != null -> CenterBox(padding) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(errorMessage.orEmpty(), color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(8.dp))
                    TextButton(onClick = onBack) { Text("返回") }
                }
            }
            records.isEmpty() -> CenterBox(padding) {
                Text(
                    text = "暂无检测记录",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            else -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    contentPadding = PaddingValues(vertical = 16.dp)
                ) {
                    items(records) { record ->
                        RecordItem(record = record, onClick = { onRecordClick(record.taskId) })
                    }
                }
            }
        }
    }
}

@Composable
private fun CenterBox(padding: PaddingValues, content: @Composable () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(padding),
        contentAlignment = Alignment.Center
    ) {
        content()
    }
}

@Composable
private fun RecordItem(record: DetectionResponse, onClick: () -> Unit) {
    val riskLevel = RiskLevel.fromString(record.riskLevel)
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("检测 #${record.taskId}", style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.height(4.dp))
                Text(record.label ?: record.prediction ?: "未知", style = MaterialTheme.typography.bodyMedium)
                record.fakeProbability?.let {
                    Text(
                        "伪造概率 ${(it * 100).toInt()}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                record.createdAt?.let {
                    Text(
                        it,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            Text(
                text = riskLevel.displayName,
                color = when (riskLevel) {
                    RiskLevel.LOW -> MaterialTheme.colorScheme.primary
                    RiskLevel.MEDIUM -> MaterialTheme.colorScheme.tertiary
                    RiskLevel.HIGH -> MaterialTheme.colorScheme.error
                    RiskLevel.UNKNOWN -> MaterialTheme.colorScheme.onSurfaceVariant
                },
                style = MaterialTheme.typography.labelLarge
            )
        }
    }
}
