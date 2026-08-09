from __future__ import annotations

import json

from app.constants import CONFIG_VERSION, DEFAULT_ASPECT_RATIO, DEFAULT_BACKGROUND, DEFAULT_QUALITY, DEFAULT_UI_LANGUAGE
from app.infrastructure.system.app_paths import AppPaths


class SettingsRepository:
    def __init__(self) -> None:
        self._path = AppPaths.settings_file()

    def _defaults(self) -> dict:
        return {
            "config_version": CONFIG_VERSION,
            "ui_language": DEFAULT_UI_LANGUAGE,
            "aspect_ratio": DEFAULT_ASPECT_RATIO,
            "quality": DEFAULT_QUALITY,
            "background_mode": DEFAULT_BACKGROUND,
            "output_dir": str(AppPaths.videos_dir()),
        }

    def load(self) -> dict:
        defaults = self._defaults()
        if not self._path.exists():
            return defaults
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            defaults.update({key: value for key, value in data.items() if key in defaults})
        except Exception:
            pass
        defaults["config_version"] = CONFIG_VERSION
        if defaults["ui_language"] not in {"es", "en"}:
            defaults["ui_language"] = DEFAULT_UI_LANGUAGE
        if not str(defaults["output_dir"]).strip():
            defaults["output_dir"] = str(AppPaths.videos_dir())
        return defaults

    def save(self, settings: dict) -> None:
        payload = self._defaults()
        payload.update({key: value for key, value in settings.items() if key in payload})
        payload["config_version"] = CONFIG_VERSION
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(self._path)
