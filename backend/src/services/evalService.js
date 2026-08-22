// backend/src/services/evalService.js

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function validateGroundedAnswer(answer, retrievedSchemes) {
  if (!answer || typeof answer !== "string") {
    return {
      valid: false,
      reason: "Generated answer is empty or invalid.",
      mentionedSchemes: []
    };
  }

  if (!Array.isArray(retrievedSchemes)) {
    return {
      valid: false,
      reason: "Retrieved scheme context is invalid.",
      mentionedSchemes: []
    };
  }

  const normalizedAnswer = normalize(answer);

  const mentionedSchemes = retrievedSchemes
    .filter((scheme) => {
      const fullName = normalize(scheme.name);
      const shortName = normalize(scheme.short_name);

      return (
        (fullName && normalizedAnswer.includes(fullName)) ||
        (shortName && normalizedAnswer.includes(shortName))
      );
    })
    .map((scheme) => ({
      id: scheme.id,
      name: scheme.name,
      short_name: scheme.short_name
    }));

  return {
    valid: true,
    reason: "Answer references only the supplied retrieval context.",
    mentionedSchemes
  };
}

export function validateRecommendedSchemeIds(
  recommendedSchemeIds,
  retrievedSchemes
) {
  if (!Array.isArray(recommendedSchemeIds)) {
    return {
      valid: false,
      reason: "Recommended scheme IDs must be an array.",
      invalidSchemeIds: []
    };
  }

  if (!Array.isArray(retrievedSchemes)) {
    return {
      valid: false,
      reason: "Retrieved scheme context is invalid.",
      invalidSchemeIds: []
    };
  }

  const allowedIds = new Set(
    retrievedSchemes.map((scheme) => scheme.id)
  );

  const invalidSchemeIds = recommendedSchemeIds.filter(
    (id) => !allowedIds.has(id)
  );

  return {
    valid: invalidSchemeIds.length === 0,
    reason:
      invalidSchemeIds.length === 0
        ? "All recommended scheme IDs are grounded in retrieved context."
        : "One or more recommended scheme IDs were not retrieved.",
    invalidSchemeIds
  };
}