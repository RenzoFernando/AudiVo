from __future__ import annotations

import shutil
from pathlib import Path


class FFmpegProvider:
    @staticmethod
    def executable() -> str:
        try:
            import imageio_ffmpeg

            bundled = Path(imageio_ffmpeg.get_ffmpeg_exe())
            if bundled.exists():
                return str(bundled)
        except Exception:
            pass
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg
        raise RuntimeError("No fue posible localizar FFmpeg.")
