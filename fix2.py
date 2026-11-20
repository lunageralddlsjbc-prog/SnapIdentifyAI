from pathlib import Path
def w(p,c):
    Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(c.strip('\n'))

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

object ResultHolder { var response: IdentifyResponse? = null }""")

w("backend/server.js","""
const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();
const app = express();
app.use(cors());
app.use(express.json({ limit: '15mb' }));
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-flash-latest" });
app.get('/health', (req, res) => res.json({ ok: true, model: "gemini-flash-latest" }));
app.get('/', (req, res) => res.json({ ok: true, service: 'snapidentify-proxy' }));
app.post('/api/identify', async (req, res) => {
  try {
    const { imageBase64 } = req.body;
    if (!imageBase64) return res.status(400).json({ error: 'No image provided' });
    const prompt = "Identify the main object in this image. Respond ONLY with valid JSON, no markdown fences, exactly: {\"objectName\":\"\",\"scientificName\":null,\"category\":\"\",\"description\":\"\",\"confidence\":0.9}. If unclear, set confidence below 0.5 and state uncertainty in description.";
    const result = await model.generateContent([prompt, { inlineData: { data: imageBase64, mimeType: "image/jpeg" } }]);
    let text = result.response.text().replace(/```json|```/g, '').trim();
    try { res.json(JSON.parse(text)); }
    catch (e) { res.status(500).json({ error: "Bad JSON from model", raw: text.slice(0, 300) }); }
  } catch (error) {
    console.error("AI Error:", error);
    res.status(500).json({ error: "Failed to identify: " + (error.message || "unknown") });
  }
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Proxy running on port " + PORT));""")

print("✅ fix2 written")
