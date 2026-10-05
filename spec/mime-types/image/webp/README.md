# image/webp (WebP Image Format)

- **Canonical MIME Type:** `image/webp`
- **File Extensions:** `.webp`
- **Applicable Standards:** Google WebP Container Specification (RIFF)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/webp` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **RIFF Chunk `XMP `**:
   Set `XMP` flag bit (0x04) in `VP8X` header chunk.
   Append chunk with FourCC `'XMP '` containing XMP packet with wellmanifest schema.
2. **RIFF Chunk `EXIF`**:
   Store standard EXIF buffer with UserComment.

---

## 3. Reading Algorithm
- Read RIFF chunk list, parse `'XMP '` or `'EXIF'` chunk data.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
