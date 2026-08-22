// backend/src/testSchemeSource.js

import { fetchAndNormalizeScheme } from "./services/schemeSourceService.js";

async function main() {
  try {
    const scheme = await fetchAndNormalizeScheme(
      "pradhan-mantri-kisan-samman-nidhi"
    );

    console.log(JSON.stringify(scheme, null, 2));
  } catch (error) {
    console.error("Test failed:", error.message);
    process.exitCode = 1;
  }
}

main();