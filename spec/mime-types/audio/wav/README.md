# audio/wav (Waveform Audio File Format)

- **Canonical MIME Type:** `audio/wav`
- **File Extensions:** `.wav`
- **Applicable Standards:** IBM/Microsoft RIFF / EBU BWF

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `audio/wav` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **RIFF Chunk `id3 `**:
   Embedded ID3v2 tag with `TXXX:WELLMANIFEST_METAFILE`.
2. **RIFF `INFO` List Chunk**:
   `ISBJ` (Subject) set to `docId`, `ICMT` (Comment) set to JSON.

---

## 3. Reading Algorithm
- Parse RIFF chunks for `'id3 '` or `'INFO'` sub-chunks.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
