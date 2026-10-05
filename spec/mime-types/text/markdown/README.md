# text/markdown (Markdown Document)

- **Canonical MIME Type:** `text/markdown`
- **File Extensions:** `.md`
- **Applicable Standards:** CommonMark / GFM

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `text/markdown` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **YAML Frontmatter (RFC / Jekyll / Hugo standard)**:
   ```markdown
   ---
   wellmanifest:
     schema: wellmanifest.metafile/v1
     docId: DOC-FV-3A0C5BB3A175D4A4
     accounting:
       amount: "250.00"
       currency: "PLN"
       contractor: "BOTERM"
   ---
   # Document content...
   ```
2. **HTML Comment**:
   `<!-- wellmanifest:metafile:v1 {"docId": "DOC-123"} -->`

---

## 3. Reading Algorithm
- Extract YAML frontmatter block between initial `---` delimiters.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
