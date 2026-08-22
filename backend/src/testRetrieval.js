// backend/src/testRetrieval.js

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { retrieveRelevantSchemes } from "./services/retrievalService.js";

const schemesFileUrl = new URL("./data/schemes.json", import.meta.url);

async function main() {
  try {
    const fileContent = await readFile(
      fileURLToPath(schemesFileUrl),
      "utf-8"
    );

    const schemes = JSON.parse(fileContent);

    const query = "I am a farmer and I need crop insurance";

    const results = retrieveRelevantSchemes(query, schemes, 5);

    console.log(`Query: ${query}`);
    console.log("");

    results.forEach((scheme, index) => {
      console.log(
        `${index + 1}. ${scheme.short_name} - score: ${scheme.score}`
      );
    });
  } catch (error) {
    console.error("Retrieval test failed:", error.message);
    process.exitCode = 1;
  }
}

main();