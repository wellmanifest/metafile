# Office Open XML (.docx, .xlsx, .pptx)

- **Canonical MIME Type:** `application/vnd.openxmlformats`
- **File Extensions:** `.docx, .xlsx, .pptx`
- **Applicable Standards:** ISO/IEC 29500 / ECMA-376

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/vnd.openxmlformats` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Custom Document Properties (`docProps/custom.xml`)**:
   Store properties in `<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties">`:
   - Property `WellmanifestDocId` (vt:lpwstr)
   - Property `WellmanifestAmount` (vt:lpwstr)
   - Property `WellmanifestJSON` (vt:lpwstr - raw payload)
2. **Custom XML Data Storage Part (`customXml/item1.xml`)**:
   Attach canonical XML or JSON payload as an independent document part.

---

## 3. Reading Algorithm
- Open zip archive of OOXML, parse `docProps/custom.xml` or custom XML part.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
