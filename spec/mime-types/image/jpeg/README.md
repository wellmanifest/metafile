# image/jpeg (Joint Photographic Experts Group)

- **Canonical MIME Type:** `image/jpeg`
- **File Extensions:** `.jpg, .jpeg`
- **Applicable Standards:** ISO/IEC 10918-1 / JEITA CP-3451 (EXIF) / ISO 16684-1 (XMP)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/jpeg` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **APP1 Marker - XMP Packet (`http://ns.adobe.com/xap/1.0/`)**:
   Embed RDF/XML containing namespace `https://wellmanifest.org/schemas/metafile/v1/`.
2. **APP1 Marker - EXIF `UserComment` (Tag 0x9286)**:
   Store UTF-8 JSON prefixed with `UNICODE` in tag 37510.
3. **APP2 / APP13 IPTC Photoshop Marker**:
   Store `Caption/Abstract` or custom record with `docId`.

---

## 3. Reading Algorithm
- Scan APP1 segments for XMP URI or parse EXIF UserComment using Pillow / piexif.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
