package com.snapidentify.ai.ui.screens
import android.graphics.Bitmap
import android.util.Base64
import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.snapidentify.ai.data.AppDatabase
import com.snapidentify.ai.data.HistoryEntity
import com.snapidentify.ai.network.IdentifyRequest
import com.snapidentify.ai.network.RetrofitClient
import com.snapidentify.ai.ui.theme.CyanAccent
import com.snapidentify.ai.ui.theme.DeepNavy
import com.snapidentify.ai.ui.theme.TextPrimary
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream

@Composable
fun ScanningScreen(navController: NavController) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val scope = rememberCoroutineScope()
    var isScanning by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val infiniteTransition = rememberInfiniteTransition(label = "scan")
    val scanOffset by infiniteTransition.animateFloat(
        initialValue = 0f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1500), RepeatMode.Reverse),
        label = "scanLine"
    )

    LaunchedEffect(Unit) {
        val bitmap = ImageHolder.bitmap
        if (bitmap == null) {
            navController.popBackStack()
            return@LaunchedEffect
        }

        try {
            val baos = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.JPEG, 80, baos)
            val base64Image = Base64.encodeToString(baos.toByteArray(), Base64.NO_WRAP)

            val response = RetrofitClient.apiService.identifyObject(IdentifyRequest(base64Image))
            
            if (response.error != null) {
                errorMessage = response.error
            } else {
                // Save to DB
                val db = AppDatabase.getDatabase(context)
                db.historyDao().insertHistory(
                    HistoryEntity(
                        objectName = response.objectName,
                        category = response.category,
                        imageUrl = "", // Can be saved to internal storage later
                        description = response.description
                    )
                )
                ResultHolder.response = response
                navController.navigate("result")
            }
        } catch (e: Exception) {
            errorMessage = "Network error: ${e.message}"
        }
        isScanning = false
    }

    Box(modifier = Modifier.fillMaxSize().background(DeepNavy), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("Analyzing with AI...", color = TextPrimary, style = androidx.compose.material3.MaterialTheme.typography.titleLarge)
            Spacer(modifier = Modifier.height(24.dp))
            CircularProgressIndicator(color = CyanAccent, modifier = Modifier.size(48.dp))
            
            if (errorMessage != null) {
                Spacer(modifier = Modifier.height(16.dp))
                Text(errorMessage!!, color = androidx.compose.ui.graphics.Color.Red)
            }
        }
    }
}

object ResultHolder {
    var response: com.snapidentify.ai.network.IdentifyResponse? = null
}