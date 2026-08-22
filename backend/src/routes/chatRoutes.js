// backend/src/routes/chatRoutes.js

import { Router } from "express";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { generateStructuredResponse } from "../services/geminiService.js";
import { retrieveRelevantSchemes } from "../services/retrievalService.js";
import {
  validateGroundedAnswer,
  validateRecommendedSchemeIds
} from "../services/evalService.js";

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

function buildGroundedPrompt(userQuery, schemes) {
  const schemeContext = schemes
    .map((scheme, index) => {
      return `
SCHEME ${index + 1}
ID: ${scheme.id}
Name: ${scheme.name}
Short Name: ${scheme.short_name}
Category: ${scheme.category.join(", ")}
Target Groups: ${scheme.target_groups.join(", ")}
Eligibility Summary: ${scheme.eligibility?.summary || "Not available"}

Important Conditions:
${(scheme.eligibility?.important_conditions || [])
  .map((condition) => `- ${condition}`)
  .join("\n")}

Benefits: ${scheme.benefits}
Application Process: ${scheme.application_process}
Source: ${scheme.official_source}
`;
    })
    .join("\n");

  return `
You are Yojana Mitra, an assistant that helps users discover Indian government welfare schemes.

STRICT RULES:

1. Answer ONLY using the scheme information provided below.
2. Do NOT invent any scheme.
3. Do NOT invent eligibility conditions, benefits, amounts, deadlines, or application processes.
4. Do NOT use general knowledge to recommend additional government schemes.
5. Do NOT claim that the user is definitely eligible unless the provided information proves it.
6. Use phrases such as "may be eligible" or "may be relevant" when eligibility is uncertain.
7. If important user information is missing, mention what information is required.
8. If none of the supplied schemes are relevant, clearly say so.
9. Keep the answer clear and practical.
10. Remind the user to verify final eligibility using the official government source.

OUTPUT RULES:

11. Return valid JSON only.
12. Return exactly these fields:
    "answer": string
    "recommended_scheme_ids": array of strings
13. Every ID inside "recommended_scheme_ids" MUST come from the retrieved scheme data below.
14. Never invent a scheme ID.
15. If no scheme should be recommended, return an empty array.

USER QUESTION:
${userQuery}

RETRIEVED SCHEME DATA:
${schemeContext}
`.trim();
}

router.post("/", async (req, res) => {
  try {
    const { message } = req.body;

    if (
      !message ||
      typeof message !== "string" ||
      !message.trim()
    ) {
      return res.status(400).json({
        error: "A valid message is required."
      });
    }

    const schemes = await loadSchemes();

    const relevantSchemes = retrieveRelevantSchemes(
      message.trim(),
      schemes,
      5,
      8
    );

    if (relevantSchemes.length === 0) {
      return res.status(200).json({
        answer:
          "I could not find a sufficiently relevant scheme in the currently available scheme data. Please provide more details such as your occupation, age, state, income range, or the type of assistance you need.",
        grounding: {
          valid: true,
          recommendedSchemeIds: [],
          mentionedSchemes: []
        },
        schemes: []
      });
    }

    const prompt = buildGroundedPrompt(
      message.trim(),
      relevantSchemes
    );

    const structuredResponse =
      await generateStructuredResponse(prompt);

    const answer = structuredResponse.answer;

    const recommendedSchemeIds =
      structuredResponse.recommended_scheme_ids;

    if (!answer || typeof answer !== "string") {
      return res.status(502).json({
        error: "Gemini returned an invalid structured response."
      });
    }

    const idValidation = validateRecommendedSchemeIds(
      recommendedSchemeIds,
      relevantSchemes
    );

    if (!idValidation.valid) {
      return res.status(502).json({
        error:
          "Generated recommendations failed grounding validation.",
        invalidSchemeIds: idValidation.invalidSchemeIds
      });
    }

    const answerValidation = validateGroundedAnswer(
      answer,
      relevantSchemes
    );

    if (!answerValidation.valid) {
      return res.status(502).json({
        error: "Generated answer failed grounding validation."
      });
    }

    return res.status(200).json({
      answer,
      grounding: {
        valid: true,
        recommendedSchemeIds,
        mentionedSchemes:
          answerValidation.mentionedSchemes
      },
      schemes: relevantSchemes.map((scheme) => ({
        id: scheme.id,
        name: scheme.name,
        short_name: scheme.short_name,
        score: scheme.score,
        official_source: scheme.official_source
      }))
    });
  } catch (error) {
    console.error("Chat route error:", error);

    return res.status(500).json({
      error: "Unable to generate a response."
    });
  }
});

export default router;