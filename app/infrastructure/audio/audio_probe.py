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

    def duration(self, path: Path) -> float | None:
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
            return None
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stdout or "")
        if not match:
            return None
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        return (hours * 3600) + (minutes * 60) + seconds
