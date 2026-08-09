from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionRequest:
    input_path: Path
    output_path: Path
    resolution: tuple[int, int]
    quality: str
    background_mode: str
    background_image: Path | None
    duration: float
