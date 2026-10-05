# video/x-matroska (Matroska / WebM Video)

- **Canonical MIME Type:** `video/x-matroska`
- **File Extensions:** `.mkv, .webm`
- **Applicable Standards:** IETF RFC 8794 (EBML) / Matroska Specification

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `video/x-matroska` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Matroska `Tags` Element (0x1254C367)**:
   Add `SimpleTag` with `TagName: WELLMANIFEST_METAFILE` and `TagString: <json>`.
2. **Attached File (`Attachments` element)**:
   File name `metafile.json`, MIME `application/json`.

---

## 3. Reading Algorithm
- Read Matroska EBML `Tags` master element or extract attachment `metafile.json`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
