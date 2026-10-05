# application/zip (ZIP Archive)

- **Canonical MIME Type:** `application/zip`
- **File Extensions:** `.zip`
- **Applicable Standards:** PKWARE APPNOTE / ISO/IEC 21320-1

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/zip` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Standard `META-INF/metafile.json`**:
   Store the canonical metadata file inside the archive under `META-INF/metafile.json` or `.wellmanifest/metafile.json`.
2. **Archive Header Comment**:
   Store JSON string in the central directory End-of-Central-Directory (EOCD) archive comment field.

---

## 3. Reading Algorithm
- Open ZIP with `zipfile`, read `META-INF/metafile.json` or `.wellmanifest/metafile.json`.
- Fall back to reading archive comment from EOCD.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
