# application/json (JavaScript Object Notation)

- **Canonical MIME Type:** `application/json`
- **File Extensions:** `.json`
- **Applicable Standards:** RFC 8259

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/json` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Top-Level Envelope Property (`_metafile` or `$metafile`)**:
   In structured JSON objects, inject a reserved top-level key:
   ```json
   {
     "$metafile": {
       "schema": "wellmanifest.metafile/v1",
       "docId": "DOC-FV-3A0C5BB3A175D4A4",
       "accounting": { "amount": "250.00", "currency": "PLN" }
     },
     "data": { }
   }
   ```
2. **JSON-LD / Schema.org Context**:
   Use `@context: "https://wellmanifest.org/contexts/metafile/v1.jsonld"`

---

## 3. Reading Algorithm
- Parse JSON AST and inspect root properties for `$metafile` or `_metafile`.
- Validate against `metafile.v1.schema.json`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
