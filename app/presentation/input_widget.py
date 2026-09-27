from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.constants import MODE_AUDIO_TO_VIDEO, MODE_VIDEO_TO_AUDIO, SUPPORTED_AUDIO_EXTENSIONS
from app.presentation.translations import tr


class AudioInputWidget(QFrame):
    files_selected = Signal(list)
    browse_requested = Signal()
    mode_toggle_requested = Signal()

    def __init__(self, ui_language: str = "es", conversion_mode: str = MODE_AUDIO_TO_VIDEO, parent=None) -> None:
        super().__init__(parent)
        self._ui_language = ui_language
        self._conversion_mode = conversion_mode
        self.setObjectName("audioInput")
        self.setAcceptDrops(True)
        self.setProperty("dragActive", False)
        self.setFixedHeight(116)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 10, 16, 10)
        root.setSpacing(3)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label = QLabel()
        self.title_label.setObjectName("dropTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.helper_label = QLabel()
        self.helper_label.setObjectName("inputHelperLabel")
        self.helper_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.helper_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.formats_label = QLabel()
        self.formats_label.setObjectName("mutedLabel")
        self.formats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formats_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch(1)
        self.mode_button = QPushButton()
        self.mode_button.setObjectName("secondaryButton")
        self.mode_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mode_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        actions.addWidget(self.mode_button)
        self.browse_button = QPushButton()
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        actions.addWidget(self.browse_button)
        actions.addStretch(1)
        root.addWidget(self.title_label)
        root.addWidget(self.helper_label)
        root.addWidget(self.formats_label)
        root.addSpacing(2)
        root.addLayout(actions)
        self.mode_button.clicked.connect(self.mode_toggle_requested.emit)
        self.browse_button.clicked.connect(self.browse_requested.emit)
        self._refresh_text()

    def set_ui_language(self, ui_language: str) -> None:
        self._ui_language = ui_language
        self._refresh_text()

    def set_mode(self, conversion_mode: str) -> None:
        self._conversion_mode = conversion_mode
        self._refresh_text()

    def set_interactions_enabled(self, enabled: bool) -> None:
        self.setAcceptDrops(enabled)
        self.mode_button.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)

    def _refresh_text(self) -> None:
        if self._conversion_mode == MODE_VIDEO_TO_AUDIO:
            self.title_label.setText(tr(self._ui_language, "drop_video_title"))
            self.helper_label.setText(tr(self._ui_language, "drop_video_helper"))
            self.formats_label.setText("MP4 · MKV · MOV · AVI · WEBM · …")
            self.browse_button.setText(tr(self._ui_language, "select_video"))
            self.mode_button.setText(tr(self._ui_language, "mode_video_to_audio"))
            self.mode_button.setToolTip(tr(self._ui_language, "switch_to_audio_to_video"))
        else:
            self.title_label.setText(tr(self._ui_language, "drop_title"))
            self.helper_label.setText(tr(self._ui_language, "drop_helper"))
            self.formats_label.setText("MP3 · M4A · WAV · FLAC · AAC · OGG")
            self.browse_button.setText(tr(self._ui_language, "select_audio"))
            self.mode_button.setText(tr(self._ui_language, "mode_audio_to_video"))
            self.mode_button.setToolTip(tr(self._ui_language, "switch_to_video_to_audio"))

    def _supported_paths(self, event) -> list[str]:
        paths: list[str] = []
        if not event.mimeData().hasUrls():
            return paths
        for url in event.mimeData().urls():
            if not url.isLocalFile():
                continue
            path = Path(url.toLocalFile())
            if not path.is_file():
                continue
            if self._conversion_mode == MODE_VIDEO_TO_AUDIO or path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                paths.append(str(path))
        return paths

    def dragEnterEvent(self, event) -> None:
        if self._supported_paths(event):
            event.acceptProposedAction()
            self._set_drag_active(True)
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if self._supported_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._set_drag_active(False)
        event.accept()

    def dropEvent(self, event) -> None:
        self._set_drag_active(False)
        paths = self._supported_paths(event)
        if paths:
            self.files_selected.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _set_drag_active(self, active: bool) -> None:
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)
