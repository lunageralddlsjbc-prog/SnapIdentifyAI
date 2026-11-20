const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

app.post('/api/identify', async (req, res) => {
  try {
    const { imageBase64 } = req.body;
    if (!imageBase64) return res.status(400).json({ error: 'No image provided' });

    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `Identify the main object in this image. Respond ONLY in this exact JSON format:
    {
      "objectName": "Name of object",
      "scientificName": "Scientific name if applicable, else null",
      "category": "Category (e.g., Plant, Animal, Electronics)",
      "description": "A detailed, 2-3 sentence description.",
      "confidence": 0.95
    }
    If unsure, set confidence below 0.5 and state uncertainty in description.`;

    const result = await model.generateContent([
      prompt,
      { inlineData: { data: imageBase64, mimeType: "image/jpeg" } }
    ]);

    const responseText = result.response.text();
    // Clean up markdown code blocks if Gemini adds them
    const cleanJson = responseText.replace(/```json\n|\n```/g, '').trim();
    
    res.json(JSON.parse(cleanJson));
  } catch (error) {
    console.error("AI Error:", error);
    res.status(500).json({ error: "Failed to identify object" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Proxy running on port ${PORT}`));