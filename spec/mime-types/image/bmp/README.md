# image/bmp (Windows Bitmap) Metafile Specification

## 1. Overview
- **MIME Type:** `image/bmp`
- **File Extensions:** `.bmp`
- **Standard:** Windows Bitmap Format

## 2. Embedding Mechanism
- BMP raster images declare explicit pixel array sizes and offsets in the `BITMAPFILEHEADER` (bytes 0–14) and `BITMAPINFOHEADER` (bytes 14–54).
- Standard image decoders read strictly up to the declared byte length.
- Metadata is appended as a non-destructive trailer chunk at the end of the file:
  ```
  [Binary BMP Header & Pixel Array]
  \n# wellmanifest-metafile:{"schema":"wellmanifest.metafile/v1","docId":"..."}\n
  ```
- This guarantees image viewing compatibility across all standard operating systems without corrupting image bits.
