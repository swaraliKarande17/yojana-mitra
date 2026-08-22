// backend/src/routes/searchRoutes.js

import { Router } from "express";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { retrieveRelevantSchemes } from "../services/retrievalService.js";

const router = Router();

const schemesFileUrl = new URL("../data/schemes.json", import.meta.url);

async function loadSchemes() {
  const fileContent = await readFile(
    fileURLToPath(schemesFileUrl),
    "utf-8"
  );

  const schemes = JSON.parse(fileContent);

  if (!Array.isArray(schemes)) {
    throw new Error("Scheme data is invalid.");
  }

  return schemes;
}

router.post("/", async (req, res) => {
  try {
    const { query } = req.body;

    if (!query || typeof query !== "string" || !query.trim()) {
      return res.status(400).json({
        error: "A valid query is required."
      });
    }

    const schemes = await loadSchemes();

    const results = retrieveRelevantSchemes(
      query.trim(),
      schemes,
      5,
      8
    );

    return res.status(200).json({
      query: query.trim(),
      count: results.length,
      results
    });
  } catch (error) {
    return res.status(500).json({
      error: "Unable to search schemes."
    });
  }
});

export default router;