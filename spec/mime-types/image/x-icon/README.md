# image/x-icon (ICO) Metafile Specification

## 1. Overview
- **MIME Type:** `image/x-icon`
- **File Extensions:** `.ico`
- **Standard:** Windows Icon Format

## 2. Embedding Mechanism
- ICO containers specify precise directory offsets and image chunk lengths for each embedded icon resolution.
- Wellmanifest metadata is appended as a non-destructive trailer chunk:
  ```
  [Binary ICO Directory and PNG/BMP Images]
  \n# wellmanifest-metafile:{"schema":"wellmanifest.metafile/v1","docId":"..."}\n
  ```
- Operating system shells and web browsers load icons by indexing the internal directory structure and ignore appended trailer metadata.
