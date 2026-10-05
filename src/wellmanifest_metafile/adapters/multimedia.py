"""Adapters for multimedia audio and video formats: MP3, FLAC, OGG, WAV, MP4, MKV, WebM."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional

from ..core import Metafile
from .image_extra import _read_trailer_metafile, _write_trailer_metafile

TAG_KEY = "WELLMANIFEST_METAFILE"


# ---------------- MP3 ----------------
def read_mp3_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        from mutagen.id3 import ID3
        audio = ID3(path)
        for frame in audio.getall("TXXX"):
            if frame.desc == TAG_KEY or "wellmanifest" in frame.desc.lower():
                val = frame.text[0] if frame.text else ""
                return Metafile.from_json(val)
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_mp3_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        from mutagen.id3 import ID3, TXXX, ID3NoHeaderError
        try:
            audio = ID3(path)
        except ID3NoHeaderError:
            audio = ID3()
        audio.add(TXXX(encoding=3, desc=TAG_KEY, text=[meta.to_json()]))
        audio.save(path)
        return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- FLAC ----------------
def read_flac_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        from mutagen.flac import FLAC
        audio = FLAC(path)
        val = audio.get(TAG_KEY) or audio.get(TAG_KEY.lower())
        if val:
            return Metafile.from_json(val[0])
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_flac_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        from mutagen.flac import FLAC
        audio = FLAC(path)
        audio[TAG_KEY] = meta.to_json()
        audio.save()
        return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- OGG ----------------
def read_ogg_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        from mutagen.oggvorbis import OggVorbis
        audio = OggVorbis(path)
        val = audio.get(TAG_KEY) or audio.get(TAG_KEY.lower())
        if val:
            return Metafile.from_json(val[0])
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_ogg_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        from mutagen.oggvorbis import OggVorbis
        audio = OggVorbis(path)
        audio[TAG_KEY] = meta.to_json()
        audio.save()
        return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- WAV ----------------
def read_wav_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        from mutagen.wave import WAVE
        audio = WAVE(path)
        if audio.tags:
            for frame in audio.tags.getall("TXXX"):
                if frame.desc == TAG_KEY or "wellmanifest" in frame.desc.lower():
                    val = frame.text[0] if frame.text else ""
                    return Metafile.from_json(val)
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_wav_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        from mutagen.wave import WAVE
        from mutagen.id3 import TXXX
        audio = WAVE(path)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(TXXX(encoding=3, desc=TAG_KEY, text=[meta.to_json()]))
        audio.save()
        return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- MP4 / M4A ----------------
def read_mp4_metafile(file_path: Path | str) -> Optional[Metafile]:
    path = Path(file_path)
    try:
        from mutagen.mp4 import MP4
        audio = MP4(path)
        tag_name = f"----:com.apple.iTunes:{TAG_KEY}"
        if tag_name in audio:
            val = audio[tag_name][0]
            if isinstance(val, bytes):
                val = val.decode("utf-8")
            return Metafile.from_json(val)
    except Exception:
        pass
    return _read_trailer_metafile(path)


def write_mp4_metafile(file_path: Path | str, meta: Metafile) -> None:
    path = Path(file_path)
    try:
        from mutagen.mp4 import MP4, MP4FreeForm
        audio = MP4(path)
        tag_name = f"----:com.apple.iTunes:{TAG_KEY}"
        audio[tag_name] = [MP4FreeForm(meta.to_json().encode("utf-8"))]
        audio.save()
        return
    except Exception:
        pass
    _write_trailer_metafile(path, meta)


# ---------------- MKV / WebM ----------------
read_mkv_metafile = _read_trailer_metafile
write_mkv_metafile = _write_trailer_metafile

read_webm_metafile = _read_trailer_metafile
write_webm_metafile = _write_trailer_metafile
