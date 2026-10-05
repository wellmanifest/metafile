# application/pdf (Portable Document Format)

- **Canonical MIME Type:** `application/pdf`
- **File Extensions:** `.pdf`
- **Applicable Standards:** ISO 32000-1 / ISO 32000-2 / PDF/A-3 (ISO 19005-3) / XMP (ISO 16684-1)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/pdf` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Document Information Dictionary (`/Info`)**:
   Standard dictionary at the trailer containing:
   - `/Title`: Human readable title
   - `/Subject`: Canonical `docId`
   - `/Keywords`: Comma-separated tags (contractor, amount, currency, URN)
   - Custom keys: `/WellmanifestDocId`, `/WellmanifestAmount`, `/WellmanifestContractor`

2. **Extensible Metadata Platform (`/Metadata` XMP Stream)**:
   ISO 16684-1 compliant RDF/XML packet embedded in the PDF Catalog (`/Root /Metadata`).
   Namespace: `xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/"`
   Properties: `wm:docId`, `wm:urn`, `wm:accountingAmount`, `wm:contractor`, `wm:jsonPayload`

3. **Self-Contained Embedded File (`/EmbeddedFiles`)**:
   PDF/A-3 specification allowing the full raw `metafile.json` to be attached inside the PDF:
   - Name: `wellmanifest-metafile.json`
   - Relationship: `/AFRelationship /Supplement`
   - MIME: `application/json`

---

## 3. Reading Algorithm
- Read `/Info` dict via standard PDF parser.
- Extract `/Metadata` stream and parse RDF/XML for `wm:*` attributes.
- Enumerate `/Names /EmbeddedFiles` for `wellmanifest-metafile.json` to obtain the complete lossless payload.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
