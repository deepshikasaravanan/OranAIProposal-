You are extracting **requirements** from a PWS/RFP-like document.
Return only “shall” statements: verbs that impose obligations on the contractor.
Ignore background/context language.

For each requirement, provide:
- section (string, e.g., "5.2.1")
- text (verbatim clause)

Call the tool `record_shall` once per requirement. If none found, do nothing.
