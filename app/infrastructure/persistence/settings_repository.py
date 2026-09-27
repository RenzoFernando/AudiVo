from __future__ import annotations

import json

from app.constants import (
    AUDIO_OUTPUT_FORMATS,
    AUDIO_PROFILES,
    CONFIG_VERSION,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_AUDIO_OUTPUT_FORMAT,
    DEFAULT_AUDIO_PROFILE,
    DEFAULT_BACKGROUND,
    DEFAULT_CONVERSION_MODE,
    DEFAULT_QUALITY,
    DEFAULT_UI_LANGUAGE,
    MODE_AUDIO_TO_VIDEO,
    MODE_VIDEO_TO_AUDIO,
)
from app.infrastructure.system.app_paths import AppPaths


class SettingsRepository:
    def __init__(self) -> None:
        self._path = AppPaths.settings_file()

    def _defaults(self) -> dict:
        return {
            "config_version": CONFIG_VERSION,
            "ui_language": DEFAULT_UI_LANGUAGE,
            "conversion_mode": DEFAULT_CONVERSION_MODE,
            "aspect_ratio": DEFAULT_ASPECT_RATIO,
            "quality": DEFAULT_QUALITY,
            "background_mode": DEFAULT_BACKGROUND,
            "audio_output_format": DEFAULT_AUDIO_OUTPUT_FORMAT,
            "audio_profile": DEFAULT_AUDIO_PROFILE,
            "video_output_dir": str(AppPaths.videos_dir()),
            "audio_output_dir": str(AppPaths.audios_dir()),
        }

    def load(self) -> dict:
        defaults = self._defaults()
        if not self._path.exists():
            return defaults
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            defaults.update({key: value for key, value in data.items() if key in defaults})
            if "video_output_dir" not in data and str(data.get("output_dir", "")).strip():
                defaults["video_output_dir"] = str(data["output_dir"])
        except Exception:
            pass
        defaults["config_version"] = CONFIG_VERSION
        if defaults["ui_language"] not in {"es", "en"}:
            defaults["ui_language"] = DEFAULT_UI_LANGUAGE
        if defaults["conversion_mode"] not in {MODE_AUDIO_TO_VIDEO, MODE_VIDEO_TO_AUDIO}:
            defaults["conversion_mode"] = DEFAULT_CONVERSION_MODE
        if defaults["audio_output_format"] not in AUDIO_OUTPUT_FORMATS:
            defaults["audio_output_format"] = DEFAULT_AUDIO_OUTPUT_FORMAT
        if defaults["audio_profile"] not in AUDIO_PROFILES:
            defaults["audio_profile"] = DEFAULT_AUDIO_PROFILE
        if not str(defaults["video_output_dir"]).strip():
            defaults["video_output_dir"] = str(AppPaths.videos_dir())
        if not str(defaults["audio_output_dir"]).strip():
            defaults["audio_output_dir"] = str(AppPaths.audios_dir())
        return defaults

    def save(self, settings: dict) -> None:
        payload = self._defaults()
        payload.update({key: value for key, value in settings.items() if key in payload})
        payload["config_version"] = CONFIG_VERSION
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self._path)
