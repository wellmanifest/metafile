# audio/ogg (Ogg Vorbis) Metafile Specification

## 1. Overview
- **MIME Type:** `audio/ogg`
- **File Extensions:** `.ogg`, `.oga`
- **Standard:** Xiph.Org Ogg Vorbis Bitstream Specification

## 2. Embedding Mechanism
- In Ogg Vorbis audio files, metadata is stored natively inside the Vorbis Comment header block under the standardized key `WELLMANIFEST_METAFILE`:
  ```ini
  WELLMANIFEST_METAFILE={"schema":"wellmanifest.metafile/v1","docId":"DOC-123",...}
  ```
- Audio players (VLC, ffmpeg, web browsers) continue normal playback and display standard tags without disruption.

## 3. Tooling
- Reading and writing is supported natively via standard libraries (e.g., `mutagen.oggvorbis`) or `metafile read/write`.
