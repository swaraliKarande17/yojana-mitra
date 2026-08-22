// backend/src/services/retrievalService.js

const STOP_WORDS = new Set([
  "i",
  "am",
  "a",
  "an",
  "the",
  "and",
  "or",
  "but",
  "to",
  "for",
  "of",
  "in",
  "on",
  "with",
  "my",
  "me",
  "we",
  "our",
  "is",
  "are",
  "was",
  "were",
  "be",
  "been",
  "being",
  "need",
  "want",
  "looking",
  "get",
  "have",
  "has",
  "had"
]);

function normalizeText(value) {
  if (!value) {
    return "";
  }

  if (Array.isArray(value)) {
    return value.join(" ").toLowerCase();
  }

  if (typeof value === "object") {
    return JSON.stringify(value).toLowerCase();
  }

  return String(value).toLowerCase();
}

function tokenize(text) {
  return normalizeText(text)
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .map((token) => token.trim())
    .filter(
      (token) =>
        token.length >= 3 &&
        !STOP_WORDS.has(token)
    );
}

function hasExactTokenMatch(searchableText, token) {
  const tokens = searchableText
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .filter(Boolean);

  return tokens.includes(token);
}

function countMatches(queryTokens, value) {
  const searchableText = normalizeText(value);

  return queryTokens.reduce((score, token) => {
    if (hasExactTokenMatch(searchableText, token)) {
      return score + 1;
    }

    return score;
  }, 0);
}

function scoreScheme(queryTokens, scheme) {
  let score = 0;

  score += countMatches(queryTokens, scheme.name) * 6;
  score += countMatches(queryTokens, scheme.short_name) * 6;
  score += countMatches(queryTokens, scheme.keywords) * 5;
  score += countMatches(queryTokens, scheme.target_groups) * 4;
  score += countMatches(queryTokens, scheme.category) * 4;
  score += countMatches(queryTokens, scheme.eligibility) * 2;
  score += countMatches(queryTokens, scheme.benefits) * 2;

  return score;
}

export function retrieveRelevantSchemes(
  query,
  schemes,
  limit = 5,
  minScore = 8
) {
  if (!query || typeof query !== "string") {
    throw new Error("A valid search query is required.");
  }

  if (!Array.isArray(schemes)) {
    throw new Error("Scheme data must be an array.");
  }

  const queryTokens = tokenize(query);

  if (queryTokens.length === 0) {
    return [];
  }

  return schemes
    .map((scheme) => ({
      ...scheme,
      score: scoreScheme(queryTokens, scheme)
    }))
    .filter((scheme) => scheme.score >= minScore)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}