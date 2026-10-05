# image/png (Portable Network Graphics)

- **Canonical MIME Type:** `image/png`
- **File Extensions:** `.png`
- **Applicable Standards:** ISO/IEC 15948:2004 / W3C PNG Specification

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/png` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **`iTXt` (International Textual Data Chunk)**:
   Keyword: `wellmanifest:metafile`
   Compression flag: `0` (uncompressed UTF-8) or `1` (deflate compressed).
   Text: complete JSON serialized payload.
2. **`tEXt` Chunk**:
   Keyword: `Wellmanifest`
   Text: JSON-serialized payload (Latin-1 encoded or Base64).
3. **`eXIf` Chunk**:
   Standard EXIF chunk containing UserComment.

---

## 3. Reading Algorithm
- Parse PNG chunks before `IDAT`. When `iTXt` has keyword `wellmanifest:metafile`, extract and decode UTF-8 JSON.
- In Python Pillow: `image.text.get("wellmanifest:metafile")`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
