from pathlib import Path
def w(p,c):
    Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(c.strip('\n'))

w("app/src/main/java/com/snapidentify/ai/network/RetrofitClient.kt","""
package com.snapidentify.ai.network
import okhttp3.OkHttpClient
import okhttp3.Protocol
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
object RetrofitClient {
    // SET THIS to your REAL Render URL. Use HYPHENS, never underscores. Must end with '/'.
    // Example: https://snapidentify-proxy.onrender.com/
    const val BASE_URL = "https://YOUR_RENDER_BACKEND_URL.onrender.com/"
    fun validateBaseUrl(): String? {
        val host = BASE_URL.substringAfter("://").substringBefore("/")
        if (host.contains("_")) return "Backend URL has underscores. Render names must use hyphens (-). Rename your Render service and update BASE_URL."
        if (BASE_URL.contains("YOUR_RENDER_BACKEND_URL")) return "Backend URL not configured. Set BASE_URL in RetrofitClient.kt to your real Render URL (ending with /)."
        if (!BASE_URL.endsWith("/")) return "Backend URL must end with '/'."
        if (!BASE_URL.startsWith("https://")) return "Backend URL must start with https://."
        return null
    }
    private val client = OkHttpClient.Builder()
        .protocols(listOf(Protocol.HTTP_1_1))
        .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(90, TimeUnit.SECONDS)
        .build()
    val apiService: ApiService by lazy {
        Retrofit.Builder().baseUrl(BASE_URL).client(client)
            .addConverterFactory(GsonConverterFactory.create()).build().create(ApiService::class.java)
    }
}""")

w("app/src/main/java/com/snapidentify/ai/network/ApiService.kt","""
package com.snapidentify.ai.network
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST
interface ApiService {
    @POST("api/identify")
    suspend fun identifyObject(@Body request: IdentifyRequest): Response<IdentifyResponse>
}""")

w("app/src/main/java/com/snapidentify/ai/ui/screens/ScanningScreen.kt","""
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
        } catch (e: Exception) { errorMessage = "Image error: ${'$'}{e.message}"; return@LaunchedEffect }

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
                        404 -> "Endpoint not found (404). Confirm server.js has /api/identify and the URL path is correct."
                        else -> "Server error ${'$'}{resp.code()}: ${'$'}{errBody.take(160)}"
                    }
                }
            } catch (e: Exception) {
                val msg = e.message ?: e.javaClass.simpleName
                lastErr = if (msg.contains("Android internal error"))
                    "TLS error: backend hostname is invalid (likely an underscore). Use a Render URL with hyphens only."
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

object ResultHolder { var response: IdentifyResponse? = null }""")

w("app/src/main/java/com/snapidentify/ai/ui/screens/CameraScreen.kt","""
package com.snapidentify.ai.ui.screens
import android.Manifest
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.navigation.NavController
import com.snapidentify.ai.ui.theme.CyanAccent
import com.snapidentify.ai.ui.theme.TextPrimary
import java.io.File
import java.util.concurrent.Executors

@Composable
fun CameraScreen(navController: NavController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var hasPermission by remember { mutableStateOf(false) }
    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { hasPermission = it }
    LaunchedEffect(Unit) { permissionLauncher.launch(Manifest.permission.CAMERA) }
    if (!hasPermission) { Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { Text("Camera permission required", color = TextPrimary) }; return }
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }
    DisposableEffect(Unit) { onDispose { cameraExecutor.shutdown() } }
    Box(Modifier.fillMaxSize()) {
        AndroidView(factory = { ctx ->
            val previewView = PreviewView(ctx)
            cameraProviderFuture.addListener({
                val provider = cameraProviderFuture.get()
                val preview = Preview.Builder().build().also { it.setSurfaceProvider(previewView.surfaceProvider) }
                val imageCapture = ImageCapture.Builder().build()
                try { provider.unbindAll(); provider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, preview, imageCapture); CameraHolder.imageCapture = imageCapture }
                catch (e: Exception) { Log.e("CameraScreen", "bind failed", e) }
            }, ContextCompat.getMainExecutor(ctx))
            previewView
        }, modifier = Modifier.fillMaxSize())
        Column(Modifier.fillMaxSize().padding(bottom = 48.dp), verticalArrangement = Arrangement.Bottom, horizontalAlignment = Alignment.CenterHorizontally) {
            Button(onClick = {
                val imageCapture = CameraHolder.imageCapture ?: return@Button
                val out = ImageCapture.OutputFileOptions.Builder(File(context.cacheDir, "photo.jpg")).build()
                imageCapture.takePicture(out, ContextCompat.getMainExecutor(context), object : ImageCapture.OnImageSavedCallback {
                    override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                        val bytes = File(context.cacheDir, "photo.jpg").readBytes()
                        ImageHolder.bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                        navController.navigate("scanning")
                    }
                    override fun onError(exception: ImageCaptureException) { Log.e("CameraScreen", "capture failed", exception) }
                })
            }, modifier = Modifier.size(72.dp), shape = CircleShape, colors = ButtonDefaults.buttonColors(containerColor = CyanAccent)) {}
        }
    }
}
object CameraHolder { var imageCapture: ImageCapture? = null }
object ImageHolder { var bitmap: Bitmap? = null }""")

w("backend/server.js","""
const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();
const app = express();
app.use(cors());
app.use(express.json({ limit: '15mb' }));
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
app.get('/health', (req, res) => res.json({ ok: true }));
app.get('/', (req, res) => res.json({ ok: true, service: 'snapidentify-proxy' }));
app.post('/api/identify', async (req, res) => {
  try {
    const { imageBase64 } = req.body;
    if (!imageBase64) return res.status(400).json({ error: 'No image provided' });
    const prompt = "Identify the main object in this image. Respond ONLY with valid JSON, no markdown, exactly: {\"objectName\":\"\",\"scientificName\":null,\"category\":\"\",\"description\":\"\",\"confidence\":0.9}. If unclear, set confidence below 0.5 and state uncertainty in description.";
    const result = await model.generateContent([prompt, { inlineData: { data: imageBase64, mimeType: "image/jpeg" } }]);
    const text = result.response.text().replace(/```json|```/g, '').trim();
    res.json(JSON.parse(text));
  } catch (error) {
    console.error("AI Error:", error);
    res.status(500).json({ error: "Failed to identify: " + (error.message || "unknown") });
  }
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Proxy running on port " + PORT));""")

print("✅ Fix files written.")
