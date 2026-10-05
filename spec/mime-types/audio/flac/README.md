# audio/flac (Free Lossless Audio Codec)

- **Canonical MIME Type:** `audio/flac`
- **File Extensions:** `.flac`
- **Applicable Standards:** IETF FLAC Specification / Xiph.org Vorbis Comment

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `audio/flac` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Vorbis Comment Block**:
   Tag: `WELLMANIFEST_METAFILE=<JSON>`
   Tag: `WELLMANIFEST_DOCID=<docId>`

---

## 3. Reading Algorithm
- Read FLAC `VORBIS_COMMENT` metadata block.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
