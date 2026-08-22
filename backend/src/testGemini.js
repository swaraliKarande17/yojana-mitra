// backend/src/testGemini.js

import "dotenv/config";
import { generateText } from "./services/geminiService.js";

async function main() {
  try {
    const response = await generateText(
      "Reply with exactly this sentence: Yojana Mitra Gemini connection is working."
    );

    console.log(response);
  } catch (error) {
    console.error("Gemini test failed:", error.message);
    process.exitCode = 1;
  }
}

main();