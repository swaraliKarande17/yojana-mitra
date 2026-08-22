// backend/src/routes/chatRoutes.js

import { Router } from "express";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { retrieveRelevantSchemes } from "../services/retrievalService.js";
import { generateText } from "../services/geminiService.js";
import { validateGroundedAnswer } from "../services/evalService.js";

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
  const schemeContext = schemes.map((scheme, index) => {
    return `
SCHEME ${index + 1}
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
  }).join("\n");

  return `
You are Yojana Mitra, an assistant that helps users discover Indian government welfare schemes.

STRICT RULES:
1. Answer ONLY using the scheme information provided below.
2. Do NOT invent any scheme, eligibility condition, benefit, amount, deadline, or application process.
3. Do NOT use your general knowledge to recommend additional government schemes.
4. Do NOT claim the user is definitely eligible unless the supplied information proves it.
5. Use phrases such as "may be eligible" or "may be relevant" when eligibility is uncertain.
6. If important user information is missing, clearly mention what information is needed.
7. If none of the supplied schemes are relevant, say that no sufficiently relevant scheme was found in the available data.
8. Keep the answer clear and practical.
9. Mention the scheme name, why it may be relevant, major eligibility considerations, benefit, and application process.
10. Remind the user to verify final eligibility through the official government source.

USER QUESTION:
${userQuery}

RETRIEVED SCHEME DATA:
${schemeContext}

Answer the user's question using only the retrieved scheme data.
`.trim();
}

router.post("/", async (req, res) => {
  try {
    const { message } = req.body;

    if (!message || typeof message !== "string" || !message.trim()) {
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
        schemes: []
      });
    }

    const prompt = buildGroundedPrompt(
      message.trim(),
      relevantSchemes
    );

    const answer = await generateText(prompt);

    const validation = validateGroundedAnswer(
      answer,
      relevantSchemes
    );

    if (!validation.valid) {
      return res.status(502).json({
        error: "Generated answer failed grounding validation."
      });
    }

    return res.status(200).json({
      answer,
      grounding: {
        valid: validation.valid,
        reason: validation.reason,
        mentionedSchemes: validation.mentionedSchemes
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
        return res.status(500).json({
          error: "Unable to generate a response."
        });
      }
    });

export default router;