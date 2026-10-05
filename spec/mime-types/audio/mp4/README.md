# audio/mp4 (M4A / AAC Audio)

- **Canonical MIME Type:** `audio/mp4`
- **File Extensions:** `.m4a, .aac`
- **Applicable Standards:** ISO/IEC 14496-14 (MP4)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `audio/mp4` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **iTunes Metadata Atom (`moov.udta.meta.ilst`)**:
   Custom reverse-DNS atom `----:com.wellmanifest:metafile`.

---

## 3. Reading Algorithm
- Traverse atoms down to `moov/udta/meta/ilst/----` with name `metafile` in domain `com.wellmanifest`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
