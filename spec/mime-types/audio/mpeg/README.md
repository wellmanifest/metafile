# audio/mpeg (MP3 Audio)

- **Canonical MIME Type:** `audio/mpeg`
- **File Extensions:** `.mp3`
- **Applicable Standards:** ISO/IEC 11172-3 / ID3v2.4

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `audio/mpeg` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **ID3v2.4 User Defined Text Frame (`TXXX`)**:
   Description: `WELLMANIFEST_METAFILE`
   Value: JSON serialized payload.
2. **General Encapsulated Object (`GEOB`)**:
   MIME: `application/json`, Filename: `metafile.json`.

---

## 3. Reading Algorithm
- Read ID3v2 tag, locate frame `TXXX` with description `WELLMANIFEST_METAFILE` or `GEOB`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
