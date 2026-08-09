from __future__ import annotations

import math
import time
from pathlib import Path

from PySide6.QtCore import QThread, QTimer, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app.app_meta import APP_VERSION
from app.constants import APP_NAME, GITHUB_URL, RESOLUTIONS, SUPPORTED_AUDIO_EXTENSIONS, WINDOW_HEIGHT, WINDOW_WIDTH
from app.domain.conversion_request import ConversionRequest
from app.infrastructure.audio.audio_probe import AudioProbe
from app.infrastructure.persistence.settings_repository import SettingsRepository
from app.infrastructure.system.app_paths import AppPaths
from app.presentation.current_audio_widget import CurrentAudioWidget
from app.presentation.input_widget import AudioInputWidget
from app.presentation.progress_widget import ProgressWidget
from app.presentation.settings_widget import SettingsWidget
from app.presentation.styles import APP_STYLE
from app.presentation.translations import tr
from app.workers.conversion_worker import ConversionWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._settings_repository = SettingsRepository()
        self._settings = self._settings_repository.load()
        self._ui_language = self._settings["ui_language"]
        self._probe = AudioProbe()
        self._audio_path: Path | None = None
        self._audio_duration: float | None = None
        self._last_output_path: Path | None = None
        self._conversion_started_at: float | None = None
        self._eta_seconds: float | None = None
        self._worker: ConversionWorker | None = None
        self._thread: QThread | None = None
        self._close_requested = False
        self.setWindowTitle(APP_NAME)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(APP_STYLE)
        self._build_ui()
        self._refresh_static_text()
        self._apply_state()
        self._save_settings()

    def _build_ui(self) -> None:
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(16, 13, 16, 10)
        root.setSpacing(8)
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 2)
        brand_row.setSpacing(8)
        brand_row.addWidget(self._accent_group(True))
        brand_row.addStretch(1)
        brand = QLabel(f"{APP_NAME} v{APP_VERSION}")
        brand.setObjectName("brandLabel")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_row.addWidget(brand, 0, Qt.AlignmentFlag.AlignCenter)
        brand_row.addStretch(1)
        brand_row.addWidget(self._accent_group(False))
        root.addLayout(brand_row)
        self.input_widget = AudioInputWidget(self._ui_language)
        self.input_widget.files_selected.connect(self._select_audio)
        self.input_widget.browse_requested.connect(self._browse_audio)
        root.addWidget(self.input_widget)
        self.current_audio_widget = CurrentAudioWidget(self._ui_language)
        self.current_audio_widget.remove_requested.connect(self._clear_audio)
        root.addWidget(self.current_audio_widget)
        self.settings_widget = SettingsWidget(
            self._settings["aspect_ratio"],
            self._settings["quality"],
            self._settings["background_mode"],
            "",
            self._settings["output_dir"],
            self._ui_language,
        )
        self.settings_widget.preferences_changed.connect(self._save_settings)
        root.addWidget(self.settings_widget)
        self.progress_widget = ProgressWidget(self._ui_language)
        root.addWidget(self.progress_widget)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.convert_button = QPushButton()
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.convert_button.clicked.connect(self._start_conversion)
        self.cancel_button = QPushButton()
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cancel_button.clicked.connect(self._cancel_conversion)
        actions.addWidget(self.convert_button, 1)
        actions.addWidget(self.cancel_button)
        root.addLayout(actions)
        result_layout = QHBoxLayout()
        result_layout.setSpacing(8)
        self.open_file_button = QPushButton()
        self.open_file_button.setObjectName("openFileButton")
        self.open_file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_file_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.open_file_button.clicked.connect(self._open_last_video)
        self.open_folder_button = QPushButton()
        self.open_folder_button.setObjectName("openFolderButton")
        self.open_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.open_folder_button.clicked.connect(self._open_output_folder)
        self.language_toggle_button = QPushButton()
        self.language_toggle_button.setObjectName("languageToggleButton")
        self.language_toggle_button.setFixedSize(36, 30)
        self.language_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.language_toggle_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.language_toggle_button.clicked.connect(self._toggle_ui_language)
        result_layout.addWidget(self.open_file_button, 1)
        result_layout.addWidget(self.open_folder_button, 1)
        result_layout.addWidget(self.language_toggle_button, 0)
        root.addLayout(result_layout)
        footer = QFrame()
        footer.setObjectName("footerFrame")
        footer.setFixedHeight(32)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 0, 10, 0)
        footer_layout.setSpacing(4)
        footer_layout.addStretch(1)
        self.footer_label = QLabel()
        self.footer_label.setObjectName("footerLabel")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.footer_label)
        self.github_button = QPushButton("GitHub")
        self.github_button.setObjectName("footerLinkButton")
        self.github_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.github_button.clicked.connect(self._open_github)
        footer_layout.addWidget(self.github_button)
        self.author_label = QLabel()
        self.author_label.setObjectName("footerLabel")
        self.author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.author_label)
        footer_layout.addStretch(1)
        shell_layout.addWidget(content)
        shell_layout.addWidget(footer)
        self.setCentralWidget(shell)

    def _accent_group(self, mirrored: bool) -> QWidget:
        group = QWidget()
        group.setFixedWidth(52)
        layout = QHBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        definitions = [("accentBlue", 24), ("accentGrayStrong", 11), ("accentGraySoft", 6)]
        if mirrored:
            definitions = list(reversed(definitions))
        for name, width in definitions:
            accent = QFrame()
            accent.setObjectName(name)
            accent.setFixedSize(width, 3)
            layout.addWidget(accent, 0, Qt.AlignmentFlag.AlignVCenter)
        return group

    def _refresh_static_text(self) -> None:
        self.input_widget.set_ui_language(self._ui_language)
        self.current_audio_widget.set_ui_language(self._ui_language)
        self.settings_widget.set_ui_language(self._ui_language)
        self.progress_widget.set_ui_language(self._ui_language)
        self.convert_button.setText(tr(self._ui_language, "convert"))
        self.cancel_button.setText(tr(self._ui_language, "cancel"))
        self.open_file_button.setText(tr(self._ui_language, "open_video"))
        self.open_folder_button.setText(tr(self._ui_language, "open_folder"))
        self.language_toggle_button.setText(tr(self._ui_language, "app_language_code"))
        self.language_toggle_button.setToolTip(tr(self._ui_language, "switch_language_tooltip"))
        self.github_button.setToolTip(tr(self._ui_language, "github_tooltip"))
        self.footer_label.setText("Copyright © 2026 ·")
        self.author_label.setText("· Renzo Fernando Mosquera Daza")
        if self._worker is None:
            if self._audio_path is None:
                self.progress_widget.set_waiting()
            elif self._last_output_path is not None and self._last_output_path.exists() and self.progress_widget.progress.value() == 100:
                self.progress_widget.set_completed()
            else:
                self.current_audio_widget.set_state("selected")
                self.progress_widget.set_ready()

    def _browse_audio(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in sorted(SUPPORTED_AUDIO_EXTENSIONS))
        selected, _ = QFileDialog.getOpenFileName(
            self,
            tr(self._ui_language, "select_audio_dialog"),
            "",
            f"{tr(self._ui_language, 'audio_filter')} ({patterns})",
        )
        if selected:
            self._select_audio([selected])

    def _select_audio(self, paths: list[str]) -> None:
        if not paths or self._worker is not None:
            return
        if len(paths) > 1:
            QMessageBox.information(self, APP_NAME, tr(self._ui_language, "extra_files"))
        path = Path(paths[0])
        if not self._probe.is_supported(path):
            QMessageBox.warning(self, APP_NAME, tr(self._ui_language, "invalid_audio"))
            return
        duration = self._probe.duration(path)
        if duration is None or duration <= 0:
            QMessageBox.warning(self, APP_NAME, tr(self._ui_language, "duration_required"))
            return
        self._audio_path = path
        self._audio_duration = duration
        self.settings_widget.clear_background_image()
        self.current_audio_widget.set_audio(path, duration)
        self.current_audio_widget.set_state("selected")
        self.progress_widget.set_ready()
        self._apply_state()

    def _clear_audio(self) -> None:
        if self._worker is not None:
            return
        self._audio_path = None
        self._audio_duration = None
        self.settings_widget.clear_background_image()
        self.current_audio_widget.clear()
        self.progress_widget.set_waiting()
        self._apply_state()

    def _configured_output_dir(self) -> Path:
        value = self.settings_widget.output_dir().strip()
        return Path(value).expanduser() if value else AppPaths.videos_dir()

    def _start_conversion(self) -> None:
        if self._worker is not None or self._audio_path is None or self._audio_duration is None:
            return
        background_mode = self.settings_widget.selected_background()
        background_image_text = self.settings_widget.background_image()
        background_image = Path(background_image_text) if background_image_text else None
        if background_mode == "Imagen" and (background_image is None or not background_image.is_file()):
            QMessageBox.warning(self, APP_NAME, tr(self._ui_language, "image_required"))
            return
        aspect_ratio = self.settings_widget.selected_aspect_ratio()
        quality = self.settings_widget.selected_quality()
        resolution = RESOLUTIONS[aspect_ratio][quality]
        try:
            from app.application.conversion_service import ConversionService

            output_dir = self._configured_output_dir()
            output_dir.mkdir(parents=True, exist_ok=True)
            service = ConversionService()
            output_path = service.create_output_path(output_dir, self._audio_path)
        except Exception:
            QMessageBox.critical(self, APP_NAME, tr(self._ui_language, "ffmpeg_error"))
            return
        request = ConversionRequest(
            input_path=self._audio_path,
            output_path=output_path,
            resolution=resolution,
            quality=quality,
            background_mode=background_mode,
            background_image=background_image,
            duration=self._audio_duration,
        )
        thread = QThread(self)
        worker = ConversionWorker(request)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_progress)
        worker.status.connect(self._on_status)
        worker.completed.connect(self._on_completed)
        worker.failed.connect(self._on_failed)
        worker.cancelled.connect(self._on_cancelled)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._on_worker_finished)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        self._conversion_started_at = time.monotonic()
        self._eta_seconds = None
        detail = tr(
            self._ui_language,
            "processed_of_total_calculating",
            processed=self._format_clock(0),
            total=self._format_clock(self._audio_duration),
        )
        self.progress_widget.set_processing(0, detail)
        self._apply_state()
        self._save_settings()
        thread.start()

    def _cancel_conversion(self) -> None:
        if self._worker is None:
            return
        self.cancel_button.setEnabled(False)
        self._worker.request_cancel()

    def _on_progress(self, value: int) -> None:
        value = max(0, min(100, int(value)))
        duration = self._audio_duration
        detail = ""
        if duration and duration > 0:
            processed = min(duration, duration * value / 100.0)
            detail = tr(
                self._ui_language,
                "processed_of_total_calculating",
                processed=self._format_clock(processed),
                total=self._format_clock(duration),
            )
        if value >= 2 and value < 100 and self._conversion_started_at is not None:
            elapsed = max(0.1, time.monotonic() - self._conversion_started_at)
            raw_eta = elapsed * (100 - value) / value
            if self._eta_seconds is None:
                self._eta_seconds = raw_eta
            else:
                self._eta_seconds = self._eta_seconds * 0.72 + raw_eta * 0.28
            if duration and duration > 0:
                processed = min(duration, duration * value / 100.0)
                detail = tr(
                    self._ui_language,
                    "processed_of_total_eta",
                    processed=self._format_clock(processed),
                    total=self._format_clock(duration),
                    remaining=self._format_remaining(self._eta_seconds),
                )
        self.progress_widget.set_processing(value, detail)

    def _on_status(self, status: str) -> None:
        if status == "processing":
            self._on_progress(self.progress_widget.progress.value())

    def _on_completed(self, output_path: str) -> None:
        self._last_output_path = Path(output_path)
        self.current_audio_widget.set_state("completed")
        self.progress_widget.set_completed()

    def _on_failed(self, message: str) -> None:
        self.current_audio_widget.set_state("selected")
        self.progress_widget.set_error()
        detail = message.strip()
        if detail:
            QMessageBox.critical(self, APP_NAME, f"{tr(self._ui_language, 'conversion_error')}\n\n{detail}")
        else:
            QMessageBox.critical(self, APP_NAME, tr(self._ui_language, "conversion_error"))

    def _on_cancelled(self) -> None:
        self.current_audio_widget.set_state("selected")
        self.progress_widget.set_cancelled()

    def _on_worker_finished(self) -> None:
        self._worker = None
        self._thread = None
        self._apply_state()
        if self._close_requested:
            QTimer.singleShot(0, self.close)

    def _apply_state(self) -> None:
        busy = self._worker is not None
        has_audio = self._audio_path is not None
        self.input_widget.set_interactions_enabled(not busy)
        self.current_audio_widget.set_interactions_enabled(not busy)
        self.settings_widget.set_interactions_enabled(not busy)
        self.convert_button.setEnabled(has_audio and not busy)
        self.cancel_button.setEnabled(busy)
        self.open_file_button.setEnabled(self._last_output_path is not None and self._last_output_path.exists())
        self.open_folder_button.setEnabled(not busy)
        self.language_toggle_button.setEnabled(not busy)

    def _toggle_ui_language(self) -> None:
        if self._worker is not None:
            return
        self._ui_language = "en" if self._ui_language == "es" else "es"
        self._settings["ui_language"] = self._ui_language
        self._refresh_static_text()
        self._save_settings()

    def _open_last_video(self) -> None:
        if self._last_output_path is not None and self._last_output_path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._last_output_path)))

    def _open_output_folder(self) -> None:
        output_dir = self._configured_output_dir()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            output_dir = AppPaths.videos_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir)))

    def _open_github(self) -> None:
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def _format_remaining(self, seconds: float) -> str:
        seconds = max(0.0, float(seconds))
        if seconds < 60:
            rounded = max(5, int(math.ceil(seconds / 5.0) * 5))
            return f"{rounded} s"
        minutes = math.ceil(seconds / 60)
        if minutes < 60:
            return f"{minutes} min"
        hours, remaining_minutes = divmod(minutes, 60)
        if remaining_minutes == 0:
            return f"{hours} h"
        return f"{hours} h {remaining_minutes} min"

    def _format_clock(self, seconds: float) -> str:
        total = max(0, int(seconds))
        hours, remainder = divmod(total, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _save_settings(self) -> None:
        self._settings.update({
            "ui_language": self._ui_language,
            "aspect_ratio": self.settings_widget.selected_aspect_ratio(),
            "quality": self.settings_widget.selected_quality(),
            "background_mode": self.settings_widget.selected_background(),
            "output_dir": self.settings_widget.output_dir() or str(AppPaths.videos_dir()),
        })
        self._settings_repository.save(self._settings)

    def closeEvent(self, event) -> None:
        if self._worker is None:
            event.accept()
            return
        self._close_requested = True
        self._worker.request_cancel()
        event.ignore()
