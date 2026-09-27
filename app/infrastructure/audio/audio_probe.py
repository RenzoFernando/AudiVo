from __future__ import annotations

import re
import subprocess
from pathlib import Path

from app.constants import SUPPORTED_AUDIO_EXTENSIONS
from app.infrastructure.media.ffmpeg_provider import FFmpegProvider


class AudioProbe:
    def __init__(self) -> None:
        self._ffmpeg = FFmpegProvider.executable()

    def is_supported(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS

    def inspect_media(self, path: Path) -> tuple[float | None, bool, bool]:
        output = self._probe_output(path)
        duration = self._duration_from_output(output)
        stream_lines = [line for line in output.splitlines() if "Stream #" in line]
        has_audio = any("Audio:" in line for line in stream_lines)
        has_video = any("Video:" in line and "attached pic" not in line.casefold() for line in stream_lines)
        return duration, has_audio, has_video

    def duration(self, path: Path) -> float | None:
        return self._duration_from_output(self._probe_output(path))

    def _probe_output(self, path: Path) -> str:
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            result = subprocess.run(
                [self._ffmpeg, "-hide_banner", "-i", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creation_flags,
                check=False,
            )
        except Exception:
            return ""
        return result.stdout or ""

    def _duration_from_output(self, output: str) -> float | None:
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
        if not match:
            return None
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        return (hours * 3600) + (minutes * 60) + seconds
