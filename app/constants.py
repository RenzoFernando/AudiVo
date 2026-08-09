from __future__ import annotations

from app.app_meta import APP_DISPLAY_NAME, APP_REPOSITORY_WEB_URL, APP_VERSION

APP_NAME = APP_DISPLAY_NAME
GITHUB_URL = APP_REPOSITORY_WEB_URL
WINDOW_WIDTH = 490
WINDOW_HEIGHT = 570
CONFIG_VERSION = 1
DEFAULT_UI_LANGUAGE = "es"
DEFAULT_ASPECT_RATIO = "16:9 Horizontal"
DEFAULT_QUALITY = "720p"
DEFAULT_BACKGROUND = "Negro"
SUPPORTED_AUDIO_EXTENSIONS = {
    ".mp3",
    ".m4a",
    ".wav",
    ".aac",
    ".flac",
    ".ogg",
    ".opus",
    ".wma",
    ".aiff",
    ".amr",
}
SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
}
ASPECT_RATIOS = (
    "16:9 Horizontal",
    "9:16 Vertical",
    "1:1 Cuadrado",
    "4:3 Horizontal",
    "3:4 Vertical",
    "3:2 Horizontal",
    "2:3 Vertical",
    "21:9 Ultrapanorámico",
)
QUALITIES = ("480p", "720p", "1080p")
BACKGROUNDS = ("Negro", "Blanco", "Imagen")
RESOLUTIONS = {
    "16:9 Horizontal": {"480p": (854, 480), "720p": (1280, 720), "1080p": (1920, 1080)},
    "9:16 Vertical": {"480p": (480, 854), "720p": (720, 1280), "1080p": (1080, 1920)},
    "1:1 Cuadrado": {"480p": (480, 480), "720p": (720, 720), "1080p": (1080, 1080)},
    "4:3 Horizontal": {"480p": (640, 480), "720p": (960, 720), "1080p": (1440, 1080)},
    "3:4 Vertical": {"480p": (480, 640), "720p": (720, 960), "1080p": (1080, 1440)},
    "3:2 Horizontal": {"480p": (720, 480), "720p": (1080, 720), "1080p": (1620, 1080)},
    "2:3 Vertical": {"480p": (480, 720), "720p": (720, 1080), "1080p": (1080, 1620)},
    "21:9 Ultrapanorámico": {"480p": (1120, 480), "720p": (1680, 720), "1080p": (2520, 1080)},
}
CRF_BY_QUALITY = {"480p": "23", "720p": "22", "1080p": "20"}
