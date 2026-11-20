package com.snapidentify.ai.ui.screens

import androidx.compose.foundation.background
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
}
