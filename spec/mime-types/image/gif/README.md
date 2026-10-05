# image/gif (Graphics Interchange Format)

- **Canonical MIME Type:** `image/gif`
- **File Extensions:** `.gif`
- **Applicable Standards:** CompuServe GIF89a

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/gif` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Application Extension Block**:
   Application Identifier: `XMP Data` (8 bytes) + Auth Code: `XMP` (3 bytes).
   Contains complete XMP packet.
2. **Comment Extension Block (0xFE)**:
   Comment string: `wellmanifest:metafile:v1 <json>`.

---

## 3. Reading Algorithm
- Scan GIF blocks for Extension Introducer `0x21` with label `0xFE` (Comment) or `0xFF` (Application).

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
