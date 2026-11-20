import os
from pathlib import Path

def w(p, c):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(c.strip('\n'))

files = {
"settings.gradle.kts": """pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "SnapIdentifyAI"
include(":app")""",

"build.gradle.kts": """plugins { id("com.android.application") version "8.7.2" apply false; id("org.jetbrains.kotlin.android") version "2.0.21" apply false; id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false }""",

"gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true""",

"app/build.gradle.kts": """plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("org.jetbrains.kotlin.plugin.compose") }
android { namespace = "com.snapidentify.ai"; compileSdk = 35
  defaultConfig { applicationId = "com.snapidentify.ai"; minSdk = 26; targetSdk = 35; versionCode = 1; versionName = "1.0" }
  buildTypes { release { isMinifyEnabled = false } }
  compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
  kotlinOptions { jvmTarget = "17" }
  buildFeatures { compose = true }
}
dependencies {
  val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
  implementation(composeBom)
  implementation("androidx.core:core-ktx:1.13.1")
  implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.6")
  implementation("androidx.activity:activity-compose:1.9.3")
  implementation("androidx.compose.ui:ui")
  implementation("androidx.compose.ui:ui-graphics")
  implementation("androidx.compose.ui:ui-tooling-preview")
  implementation("androidx.compose.material3:material3")
  implementation("androidx.navigation:navigation-compose:2.8.3")
  implementation("androidx.camera:camera-core:1.4.0")
  implementation("androidx.camera:camera-camera2:1.4.0")
  implementation("androidx.camera:camera-lifecycle:1.4.0")
  implementation("androidx.camera:camera-view:1.4.0")
  implementation("com.squareup.retrofit2:retrofit:2.11.0")
  implementation("com.squareup.retrofit2:converter-gson:2.11.0")
  implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
  implementation("androidx.room:room-runtime:2.6.1")
  implementation("androidx.room:room-ktx:2.6.1")
  implementation("androidx.datastore:datastore-preferences:1.1.1")
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}""",

"app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET" />
  <uses-permission android:name="android.permission.CAMERA" />
  <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
  <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
  <uses-permission android:name="android.permission.VIBRATE" />
  <uses-feature android:name="android.hardware.camera" android:required="true" />
  <application android:allowBackup="true" android:icon="@mipmap/ic_launcher" android:label="@string/app_name" android:roundIcon="@mipmap/ic_launcher_round" android:supportsRtl="true" android:theme="@style/Theme.SnapIdentifyAI" android:usesCleartextTraffic="false">
    <activity android:name=".MainActivity" android:exported="true" android:theme="@style/Theme.SnapIdentifyAI">
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
      </intent-filter>
    </activity>
  </application>
</manifest>""",

"app/src/main/res/values/strings.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources><string name="app_name">SnapIdentify AI</string></resources>""",

"app/src/main/res/values/colors.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources><color name="midnight_black">#05050A</color></resources>""",

"app/src/main/res/values/themes.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
  <style name="Theme.SnapIdentifyAI" parent="android:Theme.Material.NoActionBar">
    <item name="android:statusBarColor">@android:color/transparent</item>
    <item name="android:navigationBarColor">@android:color/transparent</item>
    <item name="android:windowLightStatusBar">false</item>
  </style>
</resources>""",

"app/src/main/res/drawable/ic_launcher_foreground.xml": """<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
  <path android:fillColor="#8A2BE2" android:pathData="M54,54m-40,0a40,40 0,1 1,80 0a40,40 0,1 1,-80 0" />
  <path android:fillColor="#00E5FF" android:pathData="M54,54m-20,0a20,20 0,1 1,40 0a20,20 0,1 1,-40 0" />
</vector>""",

"app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml": """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
  <background android:drawable="@color/midnight_black"/>
  <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>""",

"app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml": """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
  <background android:drawable="@color/midnight_black"/>
  <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>""",

"app/src/main/java/com/snapidentify/ai/MainActivity.kt": """package com.snapidentify.ai
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
}""",

"app/src/main/java/com/snapidentify/ai/ui/theme/Color.kt": """package com.snapidentify.ai.ui.theme
import androidx.compose.ui.graphics.Color
val MidnightBlack = Color(0xFF05050A)
val DeepNavy = Color(0xFF0A0F1D)
val ElectricViolet = Color(0xFF8A2BE2)
val CyanAccent = Color(0xFF00E5FF)
val GlassWhite = Color(0x1AFFFFFF)
val TextPrimary = Color(0xFFE0E0E0)
val TextSecondary = Color(0xFFA0A0A0)""",

"app/src/main/java/com/snapidentify/ai/ui/theme/Type.kt": """package com.snapidentify.ai.ui.theme
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
val Typography = Typography(
  headlineLarge = TextStyle(fontWeight = FontWeight.Bold, fontSize = 32.sp, lineHeight = 40.sp),
  titleLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 22.sp, lineHeight = 28.sp),
  bodyLarge = TextStyle(fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp)
)""",

"app/src/main/java/com/snapidentify/ai/ui/theme/Theme.kt": """package com.snapidentify.ai.ui.theme
import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
private val DarkColorScheme = darkColorScheme(
  primary = ElectricViolet, secondary = CyanAccent, background = MidnightBlack, surface = DeepNavy,
  onPrimary = TextPrimary, onBackground = TextPrimary, onSurface = TextPrimary
)
@Composable
fun SnapIdentifyTheme(content: @Composable () -> Unit) {
  val view = LocalView.current
  if (!view.isInEditMode) {
    SideEffect {
      val window = (view.context as Activity).window
      window.statusBarColor = MidnightBlack.toArgb()
      window.navigationBarColor = MidnightBlack.toArgb()
      WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
    }
  }
  MaterialTheme(colorScheme = DarkColorScheme, typography = Typography, content = content)
}""",

"app/src/main/java/com/snapidentify/ai/ui/components/GlassCard.kt": """package com.snapidentify.ai.ui.components
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
}""",

"app/src/main/java/com/snapidentify/ai/navigation/AppNavigation.kt": """package com.snapidentify.ai.navigation
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
}""",

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
import com.snapidentify.ai.ui.theme.*
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(onNavigateToSettings: () -> Unit, onNavigateToAbout: () -> Unit) {
  Box(modifier = Modifier.fillMaxSize().background(Brush.verticalGradient(colors = listOf(MidnightBlack, DeepNavy)))) {
    Column(modifier = Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
      Spacer(modifier = Modifier.height(48.dp))
      Text(text = "SnapIdentify", style = MaterialTheme.typography.headlineLarge, color = TextPrimary, fontWeight = FontWeight.Bold)
      Text(text = "AI Vision", style = MaterialTheme.typography.titleLarge, color = CyanAccent)
      Spacer(modifier = Modifier.height(48.dp))
      Text(text = "[Camera & Scanner UI will be added in Batch 2]", color = TextSecondary)
      Spacer(modifier = Modifier.weight(1f))
      Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        TextButton(onClick = onNavigateToSettings) { Text("Settings", color = TextSecondary) }
        TextButton(onClick = onNavigateToAbout) { Text("About", color = TextSecondary) }
      }
    }
  }
}""",

"app/src/main/java/com/snapidentify/ai/ui/screens/SettingsScreen.kt": """package com.snapidentify.ai.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
@Composable
fun SettingsScreen() {
  Box(modifier = Modifier.fillMaxSize().padding(24.dp)) { Text(text = "Settings", style = MaterialTheme.typography.headlineLarge) }
}""",

"app/src/main/java/com/snapidentify/ai/ui/screens/AboutScreen.kt": """package com.snapidentify.ai.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
@Composable
fun AboutScreen() {
  Box(modifier = Modifier.fillMaxSize().padding(24.dp)) { Text(text = "About SnapIdentify AI", style = MaterialTheme.typography.headlineLarge) }
}""",

".gitignore": """*.iml
.gradle
/local.properties
/.idea
.DS_Store
/build
/captures
.externalNativeBuild
.cxx
local.properties
/app/build""",

"README.md": """# SnapIdentify AI
Premium AI-powered object identification Android application.""",

".github/workflows/build-apk.yml": """name: Build APK
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle
      - name: Grant execute permission for gradlew
        run: chmod +x gradlew
      - name: Build Debug APK
        run: ./gradlew assembleDebug
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: SnapIdentifyAI-Debug
          path: app/build/outputs/apk/debug/app-debug.apk"""
}

for path, content in files.items():
    w(path, content)
print("✅ All project files generated successfully!")
