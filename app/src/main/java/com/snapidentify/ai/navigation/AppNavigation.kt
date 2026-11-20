package com.snapidentify.ai.navigation
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
}