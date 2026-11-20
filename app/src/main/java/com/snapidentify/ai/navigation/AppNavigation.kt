package com.snapidentify.ai.navigation
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.snapidentify.ai.ui.screens.HomeScreen
import com.snapidentify.ai.ui.screens.SettingsScreen
import com.snapidentify.ai.ui.screens.AboutScreen
@Composable
fun AppNavigation() {
  val navController = rememberNavController()
  NavHost(navController = navController, startDestination = "home") {
    composable("home") { HomeScreen(onNavigateToSettings = { navController.navigate("settings") }, onNavigateToAbout = { navController.navigate("about") }) }
    composable("settings") { SettingsScreen() }
    composable("about") { AboutScreen() }
  }
}