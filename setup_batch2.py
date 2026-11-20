import os
from pathlib import Path

def w(p, c):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(c.strip('\n'))

files = {
# --- 1. DATABASE (Room) ---
"app/src/main/java/com/snapidentify/ai/data/HistoryEntity.kt": """package com.snapidentify.ai.data
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "identification_history")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val objectName: String,
    val category: String,
    val imageUrl: String,
    val timestamp: Long = System.currentTimeMillis(),
    val description: String
)""",

"app/src/main/java/com/snapidentify/ai/data/HistoryDao.kt": """package com.snapidentify.ai.data
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {
    @Query("SELECT * FROM identification_history ORDER BY timestamp DESC")
    fun getAllHistory(): Flow<List<HistoryEntity>>
    
    @Insert
    suspend fun insertHistory(history: HistoryEntity)
    
    @Query("DELETE FROM identification_history")
    suspend fun clearHistory()
}""",

"app/src/main/java/com/snapidentify/ai/data/AppDatabase.kt": """package com.snapidentify.ai.data
import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [HistoryEntity::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun historyDao(): HistoryDao
    
    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(context.applicationContext, AppDatabase::class.java, "snapidentify_db").build()
                INSTANCE = instance
                instance
            }
        }
    }
}""",

# --- 2. NETWORKING (Retrofit) ---
"app/src/main/java/com/snapidentify/ai/network/ApiService.kt": """package com.snapidentify.ai.network
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("api/identify")
    suspend fun identifyObject(@Body request: IdentifyRequest): IdentifyResponse
}""",

"app/src/main/java/com/snapidentify/ai/network/ApiModels.kt": """package com.snapidentify.ai.network
import com.google.gson.annotations.SerializedName

data class IdentifyRequest(
    @SerializedName("imageBase64") val imageBase64: String
)

data class IdentifyResponse(
    @SerializedName("objectName") val objectName: String,
    @SerializedName("scientificName") val scientificName: String?,
    @SerializedName("category") val category: String,
    @SerializedName("description") val description: String,
    @SerializedName("confidence") val confidence: Float,
    @SerializedName("error") val error: String?
)""",

"app/src/main/java/com/snapidentify/ai/network/RetrofitClient.kt": """package com.snapidentify.ai.network
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {
    // REPLACE THIS WITH YOUR RENDER.COM BACKEND URL LATER (e.g., "https://snapidentify-proxy.onrender.com/")
    // For local testing, you can use ngrok or your PC's local IP if on the same network.
    private const val BASE_URL = "https://YOUR_RENDER_BACKEND_URL.onrender.com/" 
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val client = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}""",

# --- 3. SCREENS (Camera, Scanning, Result) ---
"app/src/main/java/com/snapidentify/ai/ui/screens/CameraScreen.kt": """package com.snapidentify.ai.ui.screens
import android.Manifest
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.*
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
import java.io.ByteArrayOutputStream
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@Composable
fun CameraScreen(navController: NavController) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var hasPermission by remember { mutableStateOf(false) }
    var imageCaptured by remember { mutableStateOf<Bitmap?>(null) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted -> hasPermission = isGranted }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }

    if (!hasPermission) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("Camera permission required", color = TextPrimary)
        }
        return
    }

    if (imageCaptured != null) {
        navController.navigate("scanning")
        // In a real app, we'd pass the bitmap or URI via ViewModel or NavArgs. 
        // For simplicity, we'll use a singleton or pass base64. Let's use a simple holder.
        ImageHolder.bitmap = imageCaptured
        imageCaptured = null // reset
    }

    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }

    DisposableEffect(Unit) {
        onDispose { cameraExecutor.shutdown() }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val imageCapture = ImageCapture.Builder().build()
                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, preview, imageCapture)
                        
                        // Store imageCapture in a holder to trigger it from a Compose button
                        CameraHolder.imageCapture = imageCapture
                    } catch (e: Exception) {
                        Log.e("CameraScreen", "Use case binding failed", e)
                    }
                }, ContextCompat.getMainExecutor(ctx))
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )
        
        Column(
            modifier = Modifier.fillMaxSize().padding(bottom = 48.dp),
            verticalArrangement = Arrangement.Bottom,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(
                onClick = {
                    val imageCapture = CameraHolder.imageCapture ?: return@Button
                    val outputFileOptions = ImageCapture.OutputFileOptions.Builder(
                        java.io.File(context.cacheDir, "photo.jpg")
                    ).build()
                    imageCapture.takePicture(outputFileOptions, ContextCompat.getMainExecutor(context), object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                            val file = java.io.File(context.cacheDir, "photo.jpg")
                            val bytes = file.readBytes()
                            ImageHolder.bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                            navController.navigate("scanning")
                        }
                        override fun onError(exception: ImageCaptureException) {
                            Log.e("CameraScreen", "Photo capture failed", exception)
                        }
                    })
                },
                modifier = Modifier.size(72.dp),
                shape = androidx.compose.foundation.shape.CircleShape,
                colors = ButtonDefaults.buttonColors(containerColor = CyanAccent)
            ) {}
        }
    }
}

object CameraHolder {
    var imageCapture: ImageCapture? = null
}

object ImageHolder {
    var bitmap: Bitmap? = null
}""",

"app/src/main/java/com/snapidentify/ai/ui/screens/ScanningScreen.kt": """package com.snapidentify.ai.ui.screens
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
}""",

"app/src/main/java/com/snapidentify/ai/ui/screens/ResultScreen.kt": """package com.snapidentify.ai.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.snapidentify.ai.ui.components.GlassCard
import com.snapidentify.ai.ui.theme.*

@Composable
fun ResultScreen(navController: NavController) {
    val response = ResultHolder.response
    if (response == null) {
        LaunchedEffect(Unit) { navController.popBackStack() }
        return
    }

    Column(
        modifier = Modifier.fillMaxSize().background(MidnightBlack).padding(24.dp).verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(32.dp))
        Text("Identification Complete", style = MaterialTheme.typography.headlineLarge, color = CyanAccent)
        Spacer(modifier = Modifier.height(24.dp))

        GlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(20.dp)) {
                Text(response.objectName, style = MaterialTheme.typography.titleLarge, color = TextPrimary, fontWeight = FontWeight.Bold)
                if (!response.scientificName.isNullOrBlank()) {
                    Text("(${response.scientificName})", style = MaterialTheme.typography.bodyLarge, color = TextSecondary)
                }
                Spacer(modifier = Modifier.height(8.dp))
                Text("Category: ${response.category}", color = CyanAccent)
                Spacer(modifier = Modifier.height(16.dp))
                Text(response.description, color = TextPrimary, style = MaterialTheme.typography.bodyLarge)
                Spacer(modifier = Modifier.height(16.dp))
                Text("Confidence: ${(response.confidence * 100).toInt()}%", color = TextSecondary)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceEvenly) {
            Button(onClick = { navController.navigate("home") { popUpTo("home") { inclusive = true } } }) {
                Text("Scan Another")
            }
            OutlinedButton(onClick = { navController.popBackStack() }) {
                Text("Back")
            }
        }
    }
}""",

# --- 4. UPDATE NAVIGATION ---
"app/src/main/java/com/snapidentify/ai/navigation/AppNavigation.kt": """package com.snapidentify.ai.navigation
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.snapidentify.ai.ui.screens.*

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "home") {
        composable("home") { HomeScreen(onNavigateToSettings = { navController.navigate("settings") }, onNavigateToAbout = { navController.navigate("about") }, onNavigateToCamera = { navController.navigate("camera") }) }
        composable("camera") { CameraScreen(navController = navController) }
        composable("scanning") { ScanningScreen(navController = navController) }
        composable("result") { ResultScreen(navController = navController) }
        composable("settings") { SettingsScreen() }
        composable("about") { AboutScreen() }
    }
}""",

# --- 5. UPDATE HOME SCREEN TO ADD CAMERA BUTTON ---
"app/src/main/java/com/snapidentify/ai/ui/screens/HomeScreen.kt": """package com.snapidentify.ai.ui.screens
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.snapidentify.ai.ui.components.GlassCard
import com.snapidentify.ai.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(onNavigateToSettings: () -> Unit, onNavigateToAbout: () -> Unit, onNavigateToCamera: () -> Unit) {
  Box(modifier = Modifier.fillMaxSize().background(Brush.verticalGradient(colors = listOf(MidnightBlack, DeepNavy)))) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
      Spacer(modifier = Modifier.height(48.dp))
      Text(text = "SnapIdentify", style = MaterialTheme.typography.headlineLarge, color = TextPrimary, fontWeight = FontWeight.Bold)
      Text(text = "AI Vision", style = MaterialTheme.typography.titleLarge, color = CyanAccent)
      Spacer(modifier = Modifier.height(48.dp))
      
      GlassCard(modifier = Modifier.fillMaxWidth().height(200.dp)) {
        Box(modifier = Modifier.fillMaxSize().padding(16.dp), contentAlignment = Alignment.Center) {
          Button(onClick = onNavigateToCamera, modifier = Modifier.fillMaxWidth().height(50.dp), colors = ButtonDefaults.buttonColors(containerColor = ElectricViolet)) {
            Text("Open Camera & Identify", color = TextPrimary, fontWeight = FontWeight.Bold)
          }
        }
      }
      
      Spacer(modifier = Modifier.weight(1f))
      Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        TextButton(onClick = onNavigateToSettings) { Text("Settings", color = TextSecondary) }
        TextButton(onClick = onNavigateToAbout) { Text("About", color = TextSecondary) }
      }
    }
  }
}""",

# --- 6. SECURE BACKEND PROXY (Node.js) ---
"backend/package.json": """{
  "name": "snapidentify-proxy",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@google/generative-ai": "^0.21.0",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.19.2"
  }
}""",

"backend/server.js": """const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

app.post('/api/identify', async (req, res) => {
  try {
    const { imageBase64 } = req.body;
    if (!imageBase64) return res.status(400).json({ error: 'No image provided' });

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `Identify the main object in this image. Respond ONLY in this exact JSON format:
    {
      "objectName": "Name of object",
      "scientificName": "Scientific name if applicable, else null",
      "category": "Category (e.g., Plant, Animal, Electronics)",
      "description": "A detailed, 2-3 sentence description.",
      "confidence": 0.95
    }
    If unsure, set confidence below 0.5 and state uncertainty in description.`;

    const result = await model.generateContent([
      prompt,
      { inlineData: { data: imageBase64, mimeType: "image/jpeg" } }
    ]);

    const responseText = result.response.text();
    // Clean up markdown code blocks if Gemini adds them
    const cleanJson = responseText.replace(/```json\\n|\\n```/g, '').trim();
    
    res.json(JSON.parse(cleanJson));
  } catch (error) {
    console.error("AI Error:", error);
    res.status(500).json({ error: "Failed to identify object" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Proxy running on port ${PORT}`));""",

"backend/.env.example": """GEMINI_API_KEY=your_gemini_api_key_here"""
}

for path, content in files.items():
    w(path, content)
print("✅ Batch 2 files generated successfully!")
