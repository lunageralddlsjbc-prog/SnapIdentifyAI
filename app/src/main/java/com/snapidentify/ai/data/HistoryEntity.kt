package com.snapidentify.ai.data
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "identification_history")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val objectName: String,
    val category: String,
    val imageUrl: String,
    val timestamp: Long = System.currentTimeMillis(),
    val description: String
)