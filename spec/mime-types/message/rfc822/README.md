# message/rfc822 (Email Message Format)

- **Canonical MIME Type:** `message/rfc822`
- **File Extensions:** `.eml, .msg`
- **Applicable Standards:** RFC 5322 / RFC 2045 (MIME)

---

## 1. Overview
This specification defines how `wellmanifest.metafile/v1` metadata is embedded directly and losslessly within `message/rfc822` files, enabling 100% self-contained documents without sidecars.

---

## 2. Embedding Specification
### Embedding Strategies

1. **Custom `X-` Headers (RFC 5322)**:
   - `X-Wellmanifest-DocID`: `DOC-FV-3A0C5BB3A175D4A4`
   - `X-Wellmanifest-Type`: `faktura`
   - `X-Wellmanifest-Date`: `2026-09-07`
   - `X-Wellmanifest-Accounting`: `amount=250.00;currency=PLN;contractor=BOTERM`
   - `X-Wellmanifest-Payload-B64`: `<base64-encoded-json>`
2. **MIME Attachment**:
   Add a dedicated MIME sub-part of type `application/vnd.wellmanifest.metafile+json`.

---

## 3. Reading Algorithm
- Parse headers via standard Python `email` module; read `X-Wellmanifest-*` headers.

---

## 4. Conformance & Compatibility
- **Visual / Playback Integrity:** Embedding metadata in these standard structures MUST NOT distort visual rendering, audio playback, or standard file inspection.
- **Fail-Safe Fallback:** If an application strips or modifies chunks/atoms during re-encoding, parsers MUST fall back gracefully without corruption.
