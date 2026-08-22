// backend/src/services/schemeSourceService.js

import axios from "axios";
import * as cheerio from "cheerio";

const MYSCHEME_BASE_URL = "https://www.myscheme.gov.in";

const httpClient = axios.create({
  timeout: 10000,
  headers: {
    "User-Agent": "YojanaMitra/1.0",
    Accept: "text/html,application/xhtml+xml"
  }
});

export async function fetchSchemePage(schemeSlug) {
  if (!schemeSlug || typeof schemeSlug !== "string") {
    throw new Error("A valid scheme slug is required.");
  }

  const normalizedSlug = schemeSlug.trim();

  if (!/^[a-z0-9-]+$/.test(normalizedSlug)) {
    throw new Error("Scheme slug contains invalid characters.");
  }

  const url = `${MYSCHEME_BASE_URL}/schemes/${normalizedSlug}`;

  try {
    const response = await httpClient.get(url);

    if (!response.data || typeof response.data !== "string") {
      throw new Error("Official source returned an invalid response.");
    }

    return {
      url,
      html: response.data
    };
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error(`Scheme not found: ${normalizedSlug}`);
    }

    throw new Error(
      `Unable to fetch scheme from official source: ${error.message}`
    );
  }
}

export function extractBasicSchemeData(html, sourceUrl) {
  if (!html || typeof html !== "string") {
    throw new Error("Valid HTML content is required.");
  }

  const $ = cheerio.load(html);

  const title =
    $("h1").first().text().trim() ||
    $("title").first().text().trim() ||
    null;

  const description =
    $("meta[name='description']").attr("content")?.trim() || null;

  return {
    name: title,
    description,
    sourceUrl,
    fetchedAt: new Date().toISOString()
  };
}

export async function fetchAndNormalizeScheme(schemeSlug) {
  const { html, url } = await fetchSchemePage(schemeSlug);

  return extractBasicSchemeData(html, url);
}