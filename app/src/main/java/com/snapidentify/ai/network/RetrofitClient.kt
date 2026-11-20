package com.snapidentify.ai.network
import okhttp3.OkHttpClient
import okhttp3.Protocol
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
object RetrofitClient {
    // SET THIS to your REAL Render URL. Use HYPHENS, never underscores. Must end with '/'.
    // Example: https://snapidentify-proxy.onrender.com/
    const val BASE_URL = "https://snapidentify-proxy.onrender.com/"
    fun validateBaseUrl(): String? {
        val host = BASE_URL.substringAfter("://").substringBefore("/")
        if (host.contains("_")) return "Backend URL has underscores. Render names must use hyphens (-). Rename your Render service and update BASE_URL."
        if (BASE_URL.contains("YOUR_RENDER_BACKEND_URL")) return "Backend URL not configured. Set BASE_URL in RetrofitClient.kt to your real Render URL (ending with /)."
        if (!BASE_URL.endsWith("/")) return "Backend URL must end with '/'."
        if (!BASE_URL.startsWith("https://")) return "Backend URL must start with https://."
        return null
    }
    private val client = OkHttpClient.Builder()
        .protocols(listOf(Protocol.HTTP_1_1))
        .addInterceptor(HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(90, TimeUnit.SECONDS)
        .build()
    val apiService: ApiService by lazy {
        Retrofit.Builder().baseUrl(BASE_URL).client(client)
            .addConverterFactory(GsonConverterFactory.create()).build().create(ApiService::class.java)
    }
}