# video/mp4 (MPEG-4 Part 14)

- **Canonical MIME Type:** `video/mp4`
- **File Extensions:** `.mp4`
- **Applicable Standards:** ISO/IEC 14496-14

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `video/mp4` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **User Data Atom (`moov.udta`)**:
   Atom with type `WMET` (Wellmanifest Metadata) containing JSON string.
2. **Timed Metadata Track**:
   Dedicated metadata track for time-synchronized annotations.

---

## 3. Reading Algorithm
- Search `moov.udta` for `WMET` or reverse-DNS metadata atom.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
