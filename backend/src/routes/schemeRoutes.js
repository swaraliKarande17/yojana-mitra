// backend/src/routes/schemeRoutes.js

import { Router } from "express";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

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

router.get("/", async (req, res) => {
  try {
    const schemes = await loadSchemes();

    return res.status(200).json({
      count: schemes.length,
      schemes
    });
  } catch (error) {
    return res.status(500).json({
      error: "Unable to load scheme data."
    });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const schemes = await loadSchemes();

    const scheme = schemes.find(
      (item) => item.id === req.params.id
    );

    if (!scheme) {
      return res.status(404).json({
        error: "Scheme not found."
      });
    }

    return res.status(200).json({
      scheme
    });
  } catch (error) {
    return res.status(500).json({
      error: "Unable to load scheme data."
    });
  }
});

export default router;