# image/avif (AV1 Image File Format)

- **Canonical MIME Type:** `image/avif`
- **File Extensions:** `.avif, .heic`
- **Applicable Standards:** ISO/IEC 23000-22 (MIAF) / ISO/IEC 14496-12 (ISOBMFF)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/avif` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **ISOBMFF `meta` Box**:
   Item of type `'mime'` with content type `application/json` or item of type `'Exif'` / `'XMP '`.

---

## 3. Reading Algorithm
- Traverse ISOBMFF box hierarchy: `root -> meta -> iloc / idat`, extract item associated with MIME metadata.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
