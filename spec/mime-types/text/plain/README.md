# text/plain (Plain Text)

- **Canonical MIME Type:** `text/plain`
- **File Extensions:** `.txt`
- **Applicable Standards:** RFC 2046

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `text/plain` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Leading Header Block**:
   ```text
   # --- WELLMANIFEST METAFILE v1 ---
   # docId: DOC-123
   # amount: 250.00
   # --- END METAFILE ---
   ```
2. **Trailing Envelope Block**:
   Placed at the end of the text file to preserve clean visual inspection.

---

## 3. Reading Algorithm
- Match regex `(?s)# --- WELLMANIFEST METAFILE v1 ---
(.*?)
# --- END METAFILE ---`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
