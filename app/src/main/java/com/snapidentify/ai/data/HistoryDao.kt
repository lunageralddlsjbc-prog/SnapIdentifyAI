package com.snapidentify.ai.data
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {
    @Query("SELECT * FROM identification_history ORDER BY timestamp DESC")
    fun getAllHistory(): Flow<List<HistoryEntity>>
    
    @Insert
    suspend fun insertHistory(history: HistoryEntity)
    
    @Query("DELETE FROM identification_history")
    suspend fun clearHistory()
}