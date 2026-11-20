package com.snapidentify.ai
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.snapidentify.ai.navigation.AppNavigation
import com.snapidentify.ai.ui.theme.SnapIdentifyTheme
class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    enableEdgeToEdge()
    setContent { SnapIdentifyTheme { AppNavigation() } }
  }
}