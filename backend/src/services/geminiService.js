// backend/src/services/geminiService.js

import { GoogleGenAI } from "@google/genai";

function getGeminiClient() {
  const apiKey = process.env.GEMINI_API_KEY;

  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not configured.");
  }

  return new GoogleGenAI({
    apiKey
  });
}

export async function generateText(prompt) {
  if (!prompt || typeof prompt !== "string" || !prompt.trim()) {
    throw new Error("A valid prompt is required.");
  }

  try {
    const ai = getGeminiClient();

    const response = await ai.models.generateContent({
      model: "gemini-3.6-flash",
      contents: prompt.trim()
    });

    const text = response.text?.trim();

    if (!text) {
      throw new Error("Gemini returned an empty response.");
    }

    return text;
  } catch (error) {
    throw new Error(`Gemini request failed: ${error.message}`);
  }
}