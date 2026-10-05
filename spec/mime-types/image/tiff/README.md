# image/tiff (Tag Image File Format)

- **Canonical MIME Type:** `image/tiff`
- **File Extensions:** `.tiff, .tif`
- **Applicable Standards:** TIFF 6.0 / Adobe TIFF Specification

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/tiff` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Tag 700 (0x02BC) - XMP Metadata**:
   Direct raw XML XMP packet containing wellmanifest namespace.
2. **Tag 37510 (0x9286) - UserComment (EXIF IFD)**:
   JSON payload.
3. **Tag 270 (0x010E) - ImageDescription**:
   Human readable title with `[wellmanifest docId=...]`.

---

## 3. Reading Algorithm
- Read IFD entries for Tag 700 (XMP) or Tag 37510.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
