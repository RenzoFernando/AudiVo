from __future__ import annotations

import re
import subprocess
import threading
from collections import deque
from pathlib import Path
from typing import Callable

from app.constants import CRF_BY_QUALITY
from app.domain.conversion_request import ConversionRequest
from app.infrastructure.media.ffmpeg_provider import FFmpegProvider


class ConversionCancelled(RuntimeError):
    pass


class ConversionService:
    def __init__(self) -> None:
        self._ffmpeg = FFmpegProvider.executable()
        self._process: subprocess.Popen | None = None
        self._process_lock = threading.Lock()

    def create_output_path(self, directory: Path, input_path: Path) -> Path:
        raw_name = f"{input_path.stem}_video"
        clean_name = re.sub(r'[<>:"/\|?*]+', "_", raw_name).strip().rstrip(".")
        clean_name = clean_name or "audio_video"
        candidate = directory / f"{clean_name}.mp4"
        counter = 1
        while candidate.exists():
            candidate = directory / f"{clean_name}_{counter}.mp4"
            counter += 1
        return candidate

    def convert(
        self,
        request: ConversionRequest,
        cancel_event: threading.Event,
        progress_callback: Callable[[int], None],
        status_callback: Callable[[str], None],
    ) -> Path:
        request.output_path.parent.mkdir(parents=True, exist_ok=True)
        command = self._build_command(request)
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        tail = deque(maxlen=24)
        status_callback("processing")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creation_flags,
        )
        with self._process_lock:
            self._process = process
        try:
            if process.stdout is not None:
                for raw_line in process.stdout:
                    line = raw_line.strip()
                    if line:
                        tail.append(line)
                    if cancel_event.is_set():
                        self._stop_process(process)
                        raise ConversionCancelled()
                    if line.startswith("out_time_ms="):
                        self._emit_progress(line.split("=", 1)[1], request.duration, progress_callback)
                    elif line.startswith("out_time_us="):
                        self._emit_progress(line.split("=", 1)[1], request.duration, progress_callback)
            return_code = process.wait()
            if cancel_event.is_set():
                raise ConversionCancelled()
            if return_code != 0:
                detail = "\n".join(tail)
                raise RuntimeError(detail or "FFmpeg no pudo crear el video.")
            progress_callback(100)
            return request.output_path
        except ConversionCancelled:
            self._remove_partial(request.output_path)
            raise
        except Exception:
            self._remove_partial(request.output_path)
            raise
        finally:
            with self._process_lock:
                if self._process is process:
                    self._process = None

    def cancel(self) -> None:
        with self._process_lock:
            process = self._process
        if process is not None:
            self._stop_process(process)

    def _emit_progress(self, microseconds_text: str, duration: float, callback: Callable[[int], None]) -> None:
        if duration <= 0:
            return
        try:
            microseconds = int(microseconds_text)
        except ValueError:
            return
        seconds = microseconds / 1_000_000.0
        percent = max(0, min(99, int((seconds / duration) * 100)))
        callback(percent)

    def _build_command(self, request: ConversionRequest) -> list[str]:
        width, height = request.resolution
        size = f"{width}x{height}"
        common = [
            self._ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stats_period",
            "0.25",
        ]
        if request.background_mode == "Imagen":
            filter_value = (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"setsar=1,format=yuv420p"
            )
            common.extend([
                "-loop",
                "1",
                "-framerate",
                "30",
                "-i",
                str(request.background_image),
                "-i",
                str(request.input_path),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-vf",
                filter_value,
            ])
        else:
            color = "white" if request.background_mode == "Blanco" else "black"
            common.extend([
                "-f",
                "lavfi",
                "-i",
                f"color=c={color}:s={size}:r=30",
                "-i",
                str(request.input_path),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
            ])
        common.extend([
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-tune",
            "stillimage",
            "-crf",
            CRF_BY_QUALITY.get(request.quality, "22"),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            "-progress",
            "pipe:1",
            "-nostats",
            str(request.output_path),
        ])
        return common

    def _stop_process(self, process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return
        try:
            process.terminate()
            process.wait(timeout=1.5)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass

    def _remove_partial(self, path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass
