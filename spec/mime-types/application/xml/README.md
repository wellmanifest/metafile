# application/xml (Extensible Markup Language)

- **Canonical MIME Type:** `application/xml`
- **File Extensions:** `.xml`
- **Applicable Standards:** W3C XML 1.0

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `application/xml` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Processing Instruction or Header Comment**:
   `<?wellmanifest-metafile docId="DOC-123" amount="250.00" ?>`
   or: `<!-- wellmanifest:metafile:v1 {"docId": "DOC-123"} -->`
2. **Dedicated Child Element**:
   `<wm:metafile xmlns:wm="https://wellmanifest.org/schemas/metafile/v1/">...</wm:metafile>`

---

## 3. Reading Algorithm
- XPath search for `//wm:metafile` or parse header XML comments starting with `wellmanifest:metafile:v1`.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
