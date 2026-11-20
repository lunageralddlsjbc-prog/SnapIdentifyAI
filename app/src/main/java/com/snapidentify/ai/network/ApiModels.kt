package com.snapidentify.ai.network
import com.google.gson.annotations.SerializedName

data class IdentifyRequest(
    @SerializedName("imageBase64") val imageBase64: String
)

data class IdentifyResponse(
    @SerializedName("objectName") val objectName: String,
    @SerializedName("scientificName") val scientificName: String?,
    @SerializedName("category") val category: String,
    @SerializedName("description") val description: String,
    @SerializedName("confidence") val confidence: Float,
    @SerializedName("error") val error: String?
)