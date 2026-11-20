package com.snapidentify.ai.ui.components
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.snapidentify.ai.ui.theme.GlassWhite
@Composable
fun GlassCard(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
  Card(modifier = modifier, shape = RoundedCornerShape(24.dp), colors = CardDefaults.cardColors(containerColor = GlassWhite), border = BorderStroke(1.dp, Color.White.copy(alpha = 0.1f)), elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)) { content() }
}