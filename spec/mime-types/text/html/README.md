# text/html (Hypertext Markup Language)

- **Canonical MIME Type:** `text/html`
- **File Extensions:** `.html, .htm`
- **Applicable Standards:** W3C HTML5

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `text/html` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **`<script type="application/ld+json" id="wellmanifest-metafile">`**:
   Clean, standard-compliant JSON-LD script tag in the `<head>` or `<body>`.
2. **`<meta name="wellmanifest:*" content="...">` Tags**:
   `<meta name="wellmanifest:docId" content="DOC-123">`

---

## 3. Reading Algorithm
- Query `<script type="application/ld+json" id="wellmanifest-metafile">` or extract `<meta name="wellmanifest:...">`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
