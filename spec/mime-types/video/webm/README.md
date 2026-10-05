# video/webm (WebM Video) Metafile Specification

## 1. Overview
- **MIME Type:** `video/webm`
- **File Extensions:** `.webm`
- **Standard:** WebM Project (EBML / Matroska subset)

## 2. Embedding Mechanism
- WebM files utilize the EBML container format.
- Metadata is embedded either via standard Matroska/WebM EBML Tags (`Tag` element with `TagName="WELLMANIFEST_METAFILE"`) or as a non-destructive trailer stream at the end of the file.
- Hardware and software decoders index video clusters from the header seek table and ignore trailer data.
