# application/epub+zip (Electronic Publication)

- **Canonical MIME Type:** `application/epub+zip`
- **File Extensions:** `.epub`
- **Applicable Standards:** IDPF / W3C EPUB 3.3

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/epub+zip` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Package Document (`content.opf` / `<metadata>`)**:
   Add `<meta property="wm:docId">DOC-123</meta>` and `<link rel="wm:metafile" href="metafile.json"/>`.
2. **Container File (`META-INF/metafile.json`)**:
   Standard bundled sidecar within the EPUB OCF container.

---

## 3. Reading Algorithm
- Inspect EPUB package OPF `<metadata>` section or extract `META-INF/metafile.json`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
