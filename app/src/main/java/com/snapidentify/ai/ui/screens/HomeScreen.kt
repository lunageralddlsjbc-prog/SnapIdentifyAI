package com.snapidentify.ai.ui.screens
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
}