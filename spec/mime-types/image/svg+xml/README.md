# image/svg+xml (Scalable Vector Graphics)

- **Canonical MIME Type:** `image/svg+xml`
- **File Extensions:** `.svg`
- **Applicable Standards:** W3C SVG 1.1 / 2.0

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `image/svg+xml` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Standard `<metadata>` Element**:
   Inside `<svg>` root:
   ```xml
   <metadata id="wellmanifest-metafile">
     <wm:metafile xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/">
       {"schema": "wellmanifest.metafile/v1", "docId": "DOC-123"}
     </wm:metafile>
   </metadata>
   ```
2. **`<script type="application/ld+json">` Block**.

---

## 3. Reading Algorithm
- Parse XML, query `/svg/metadata` children or find element with ID `wellmanifest-metafile`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
