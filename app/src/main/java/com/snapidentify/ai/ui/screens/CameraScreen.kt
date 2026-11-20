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
object ImageHolder { var bitmap: Bitmap? = null }