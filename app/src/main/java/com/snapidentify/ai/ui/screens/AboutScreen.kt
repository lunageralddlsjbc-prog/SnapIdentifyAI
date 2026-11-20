package com.snapidentify.ai.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
@Composable
fun AboutScreen() {
  Box(modifier = Modifier.fillMaxSize().padding(24.dp)) { Text(text = "About SnapIdentify AI", style = MaterialTheme.typography.headlineLarge) }
}