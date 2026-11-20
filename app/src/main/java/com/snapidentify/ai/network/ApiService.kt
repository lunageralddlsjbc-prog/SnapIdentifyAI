package com.snapidentify.ai.network
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("api/identify")
    suspend fun identifyObject(@Body request: IdentifyRequest): IdentifyResponse
}