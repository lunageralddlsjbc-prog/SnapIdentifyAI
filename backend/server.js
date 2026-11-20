const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json({ limit: '15mb' }));

let genAI = null;
if (process.env.GEMINI_API_KEY) {
  genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
} else {
  console.error('GEMINI_API_KEY is not set');
}

const PROMPT = 'Identify the main object in this image. Respond ONLY with valid JSON, no markdown fences, exactly: {"objectName":"", "scientificName":null, "category":"", "description":"", "confidence":0.9}. If unclear, set confidence below 0.5 and state uncertainty in description.';

app.get('/health', (req, res) => res.json({ ok: true, model: 'gemini-flash-latest', key: genAI ? 'set' : 'missing' }));
app.get('/', (req, res) => res.json({ ok: true, service: 'snapidentify-proxy' }));

app.post('/api/identify', async (req, res) => {
  try {
    if (!genAI) return res.status(500).json({ error: 'GEMINI_API_KEY not set on Render' });
    const imageBase64 = req.body.imageBase64;
    if (!imageBase64) return res.status(400).json({ error: 'No image provided' });
    const model = genAI.getGenerativeModel({ model: 'gemini-flash-latest' });
    const result = await model.generateContent([PROMPT, { inlineData: { data: imageBase64, mimeType: 'image/jpeg' } }]);
    let text = result.response.text().replace(/```json|```/g, '').trim();
    try { res.json(JSON.parse(text)); }
    catch (e) { res.status(500).json({ error: 'Bad JSON from model', raw: text.slice(0, 300) }); }
  } catch (error) {
    console.error('AI Error:', error);
    res.status(500).json({ error: 'Failed to identify: ' + (error.message || 'unknown') });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Proxy running on port ' + PORT));