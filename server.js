require("dotenv").config();
const express = require("express");
const path = require("path");

const app = express();
app.use(express.json({ limit: "2mb" }));
app.use(express.static(__dirname));

app.post("/api/generate", async (req, res) => {
  try {
    const { prompt, style = "photorealistic", size = "1024x1024" } = req.body || {};
    if (!prompt || typeof prompt !== "string") {
      return res.status(400).json({ error: "Please enter an image description." });
    }
    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({
        error: "OPENAI_API_KEY is missing. Add it to your .env file, then restart the server."
      });
    }

    const response = await fetch("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "gpt-image-1",
        prompt: `Create an image in ${style} style. ${prompt}`,
        size,
        n: 1
      })
    });

    const result = await response.json();
    if (!response.ok) {
      return res.status(response.status).json({
        error: result.error?.message || "The AI image service returned an error."
      });
    }

    const item = result.data && result.data[0];
    if (!item || !item.b64_json) {
      return res.status(502).json({ error: "No image data was returned by the AI service." });
    }
    res.json({ image: `data:image/png;base64,${item.b64_json}` });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Unexpected server error. Please try again." });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`SnapVoice is running at http://localhost:${port}`));
