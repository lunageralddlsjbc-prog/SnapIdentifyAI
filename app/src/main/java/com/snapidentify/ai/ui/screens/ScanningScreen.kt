package com.snapidentify.ai.ui.screens
import android.graphics.Bitmap
import android.util.Base64
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.snapidentify.ai.data.AppDatabase
import com.snapidentify.ai.data.HistoryEntity
import com.snapidentify.ai.network.IdentifyRequest
import com.snapidentify.ai.network.IdentifyResponse
import com.snapidentify.ai.network.RetrofitClient
import com.snapidentify.ai.ui.theme.*
import kotlinx.coroutines.delay
import java.io.ByteArrayOutputStream

@Composable
fun ScanningScreen(navController: NavController) {
    val context = LocalContext.current
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        val bitmap = ImageHolder.bitmap
        if (bitmap == null) { navController.popBackStack(); return@LaunchedEffect }
        RetrofitClient.validateBaseUrl()?.let { errorMessage = it; return@LaunchedEffect }

        val base64Image = try {
            val scaled = scaleBitmap(bitmap, 1024)
            val baos = ByteArrayOutputStream()
            scaled.compress(Bitmap.CompressFormat.JPEG, 75, baos)
            Base64.encodeToString(baos.toByteArray(), Base64.NO_WRAP)
        } catch (e: Exception) { errorMessage = "Image error: " + e.message; return@LaunchedEffect }

        var attempt = 0; var lastErr: String? = null
        while (attempt < 2) {
            attempt++
            try {
                val resp = RetrofitClient.apiService.identifyObject(IdentifyRequest(base64Image))
                if (resp.isSuccessful) {
                    val body = resp.body()
                    if (body != null && body.error == null) {
                        AppDatabase.getDatabase(context).historyDao().insertHistory(
                            HistoryEntity(objectName = body.objectName, category = body.category, imageUrl = "", description = body.description)
                        )
                        ResultHolder.response = body; navController.navigate("result"); return@LaunchedEffect
                    } else lastErr = body?.error ?: "Empty response from AI"
                } else {
                    val errBody = resp.errorBody()?.string() ?: ""
                    lastErr = when (resp.code()) {
                        503 -> "Backend is waking up (Render free tier). Try again in ~20 seconds."
                        404 -> "Endpoint not found (404). Confirm server.js has /api/identify."
                        else -> "Server error " + resp.code() + ": " + errBody.take(200)
                    }
                }
            } catch (e: Exception) {
                val msg = e.message ?: e.javaClass.simpleName
                lastErr = if (msg.contains("Android internal error"))
                    "TLS error: backend hostname invalid (underscore). Use hyphens only."
                else msg
                if (attempt < 2) delay(2500)
            }
        }
        errorMessage = lastErr
    }

    Box(Modifier.fillMaxSize().background(DeepNavy), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(24.dp)) {
            Text("Analyzing with AI...", color = TextPrimary, style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(24.dp))
            if (errorMessage == null) CircularProgressIndicator(color = CyanAccent, modifier = Modifier.size(48.dp))
            else {
                Text(errorMessage!!, color = Color(0xFFFF6B6B), style = MaterialTheme.typography.bodyLarge)
                Spacer(Modifier.height(16.dp))
                Button(onClick = { navController.popBackStack() }) { Text("Back to Camera") }
            }
        }
    }
}

private fun scaleBitmap(src: Bitmap, maxDim: Int): Bitmap {
    val w = src.width; val h = src.height
    if (w <= maxDim && h <= maxDim) return src
    val r = maxDim.toFloat() / maxOf(w, h)
    return Bitmap.createScaledBitmap(src, (w*r).toInt().coerceAtLeast(1), (h*r).toInt().coerceAtLeast(1), true)
}

object ResultHolder { var response: IdentifyResponse? = null }