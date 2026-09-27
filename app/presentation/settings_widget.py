from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPalette, QPen
from PySide6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget

from app.constants import (
    ASPECT_RATIOS,
    AUDIO_OUTPUT_FORMATS,
    AUDIO_PROFILES,
    BACKGROUNDS,
    MODE_AUDIO_TO_VIDEO,
    MODE_VIDEO_TO_AUDIO,
    QUALITIES,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from app.infrastructure.system.app_paths import AppPaths
from app.presentation.translations import tr


class ChevronComboBox(QComboBox):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        color = QColor("#5f646d" if not self.isEnabled() else ("#ffffff" if self.underMouse() else "#cfd3da"))
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        drop_width = 27.0
        center_x = self.width() - (drop_width / 2.0)
        center_y = self.height() / 2.0
        painter.drawLine(QPointF(center_x - 4.0, center_y - 2.0), QPointF(center_x, center_y + 2.0))
        painter.drawLine(QPointF(center_x, center_y + 2.0), QPointF(center_x + 4.0, center_y - 2.0))


class CenteredDotsButton(QPushButton):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        color = QColor("#5f646d" if not self.isEnabled() else ("#ffffff" if self.underMouse() else "#cfd3da"))
        pen = QPen(color, 2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        for offset in (-4.0, 0.0, 4.0):
            painter.drawPoint(QPointF(center_x + offset, center_y))


class SettingsWidget(QWidget):
    preferences_changed = Signal()

    def __init__(
        self,
        aspect_ratio: str,
        quality: str,
        background_mode: str,
        background_image: str,
        output_dir: str,
        audio_format: str,
        audio_profile: str,
        conversion_mode: str = MODE_AUDIO_TO_VIDEO,
        ui_language: str = "es",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._ui_language = ui_language
        self._conversion_mode = conversion_mode
        self._background_image = background_image
        self._aspect_ratio = aspect_ratio
        self._quality = quality
        self._background_mode = background_mode
        self._audio_format = audio_format
        self._audio_profile = audio_profile
        self._default_output_dir = self._default_dir_for_mode(conversion_mode)
        self._output_dir = str(output_dir or self._default_output_dir)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(4)

        self.format_label = QLabel()
        self.format_label.setObjectName("sectionLabel")
        self.quality_label = QLabel()
        self.quality_label.setObjectName("sectionLabel")
        self.background_label = QLabel()
        self.background_label.setObjectName("sectionLabel")
        self.output_label = QLabel()
        self.output_label.setObjectName("sectionLabel")

        self.format_combo = ChevronComboBox()
        self.quality_combo = ChevronComboBox()
        self.background_combo = ChevronComboBox()
        self.profile_hint = QLabel()
        self.profile_hint.setObjectName("modelHintLabel")
        self.profile_hint.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.image_button = QPushButton()
        self.image_button.setObjectName("imageButton")
        self.image_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.image_button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

        self.output_edit = QLineEdit()
        output_palette = self.output_edit.palette()
        output_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#3b82f6"))
        self.output_edit.setPalette(output_palette)
        self.output_button = CenteredDotsButton()
        self.output_button.setObjectName("browseButton")
        self.output_button.setFixedWidth(36)
        self.output_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.output_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(self.format_label, 0, 0)
        layout.addWidget(self.quality_label, 0, 1)
        layout.addWidget(self.format_combo, 1, 0)
        layout.addWidget(self.quality_combo, 1, 1)
        layout.addWidget(self.background_label, 2, 0, 1, 2)
        layout.addWidget(self.profile_hint, 2, 1)
        layout.addWidget(self.background_combo, 3, 0)
        layout.addWidget(self.image_button, 3, 1)
        layout.addWidget(self.output_label, 4, 0, 1, 2)
        output_row = QHBoxLayout()
        output_row.setContentsMargins(0, 0, 0, 0)
        output_row.setSpacing(6)
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(self.output_button)
        layout.addLayout(output_row, 5, 0, 1, 2)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.format_combo.currentIndexChanged.connect(self._combo_changed)
        self.quality_combo.currentIndexChanged.connect(self._combo_changed)
        self.background_combo.currentIndexChanged.connect(self._combo_changed)
        self.image_button.clicked.connect(self._select_background_image)
        self.output_edit.editingFinished.connect(self.preferences_changed.emit)
        self.output_button.clicked.connect(self._browse_output)

        self._rebuild_controls()
        self._refresh_labels()
        self._refresh_image_button()
        self._refresh_profile_hint()

    def conversion_mode(self) -> str:
        return self._conversion_mode

    def selected_aspect_ratio(self) -> str:
        if self._conversion_mode == MODE_AUDIO_TO_VIDEO:
            return str(self.format_combo.currentData())
        return self._aspect_ratio

    def selected_quality(self) -> str:
        if self._conversion_mode == MODE_AUDIO_TO_VIDEO:
            return str(self.quality_combo.currentData())
        return self._quality

    def selected_background(self) -> str:
        if self._conversion_mode == MODE_AUDIO_TO_VIDEO:
            return str(self.background_combo.currentData())
        return self._background_mode

    def selected_audio_format(self) -> str:
        if self._conversion_mode == MODE_VIDEO_TO_AUDIO:
            return str(self.format_combo.currentData())
        return self._audio_format

    def selected_audio_profile(self) -> str:
        if self._conversion_mode == MODE_VIDEO_TO_AUDIO:
            return str(self.quality_combo.currentData())
        return self._audio_profile

    def background_image(self) -> str:
        return self._background_image

    def clear_background_image(self) -> None:
        self._background_image = ""
        self._refresh_image_button()

    def output_dir(self) -> str:
        return self._output_dir.strip() or self._default_output_dir

    def output_name(self) -> str:
        return self.output_edit.text().strip()

    def set_output_name(self, name: str) -> None:
        self.output_edit.setText(str(name or "").strip())

    def set_mode(self, conversion_mode: str, output_dir: str) -> None:
        self._capture_current_values()
        self._conversion_mode = conversion_mode
        self._default_output_dir = self._default_dir_for_mode(conversion_mode)
        self._output_dir = str(output_dir or self._default_output_dir)
        self._rebuild_controls()
        self._refresh_labels()
        self._refresh_image_button()
        self._refresh_profile_hint()

    def set_ui_language(self, ui_language: str) -> None:
        self._capture_current_values()
        self._ui_language = ui_language
        self._rebuild_controls()
        self._refresh_labels()
        self._refresh_image_button()
        self._refresh_profile_hint()

    def set_interactions_enabled(self, enabled: bool) -> None:
        self.format_combo.setEnabled(enabled)
        self.quality_combo.setEnabled(enabled)
        self.background_combo.setEnabled(enabled and self._conversion_mode == MODE_AUDIO_TO_VIDEO)
        self.image_button.setEnabled(enabled and self._conversion_mode == MODE_AUDIO_TO_VIDEO and self.selected_background() == "Imagen")
        self.output_edit.setEnabled(enabled)
        self.output_button.setEnabled(enabled)

    def _rebuild_controls(self) -> None:
        self.format_combo.blockSignals(True)
        self.quality_combo.blockSignals(True)
        self.background_combo.blockSignals(True)
        self.format_combo.clear()
        self.quality_combo.clear()
        self.background_combo.clear()

        if self._conversion_mode == MODE_VIDEO_TO_AUDIO:
            for value in AUDIO_OUTPUT_FORMATS:
                self.format_combo.addItem(value, value)
            profile_labels = {
                "Voz": tr(self._ui_language, "audio_profile_voice"),
                "Estándar": tr(self._ui_language, "audio_profile_standard"),
                "Original": tr(self._ui_language, "audio_profile_original"),
            }
            for value in AUDIO_PROFILES:
                self.quality_combo.addItem(profile_labels.get(value, value), value)
            self._select_data(self.format_combo, self._audio_format)
            self._select_data(self.quality_combo, self._audio_profile)
        else:
            aspect_labels = {
                "16:9 Horizontal": tr(self._ui_language, "aspect_16_9"),
                "9:16 Vertical": tr(self._ui_language, "aspect_9_16"),
                "1:1 Cuadrado": tr(self._ui_language, "aspect_1_1"),
                "4:3 Horizontal": tr(self._ui_language, "aspect_4_3"),
                "3:4 Vertical": tr(self._ui_language, "aspect_3_4"),
                "3:2 Horizontal": tr(self._ui_language, "aspect_3_2"),
                "2:3 Vertical": tr(self._ui_language, "aspect_2_3"),
                "21:9 Ultrapanorámico": tr(self._ui_language, "aspect_21_9"),
            }
            background_labels = {
                "Negro": tr(self._ui_language, "background_black"),
                "Blanco": tr(self._ui_language, "background_white"),
                "Imagen": tr(self._ui_language, "background_image"),
            }
            for value in ASPECT_RATIOS:
                self.format_combo.addItem(aspect_labels.get(value, value), value)
            for value in QUALITIES:
                self.quality_combo.addItem(value, value)
            for value in BACKGROUNDS:
                self.background_combo.addItem(background_labels.get(value, value), value)
            self._select_data(self.format_combo, self._aspect_ratio)
            self._select_data(self.quality_combo, self._quality)
            self._select_data(self.background_combo, self._background_mode)

        self.format_combo.blockSignals(False)
        self.quality_combo.blockSignals(False)
        self.background_combo.blockSignals(False)

    def _refresh_labels(self) -> None:
        audio_mode = self._conversion_mode == MODE_VIDEO_TO_AUDIO
        self.format_label.setText(tr(self._ui_language, "audio_format") if audio_mode else tr(self._ui_language, "format"))
        self.quality_label.setText(tr(self._ui_language, "audio_profile") if audio_mode else tr(self._ui_language, "quality"))
        self.background_label.setVisible(not audio_mode)
        self.background_combo.setVisible(not audio_mode)
        self.profile_hint.setVisible(audio_mode)
        self.image_button.setVisible(not audio_mode and self.selected_background() == "Imagen")
        self.background_label.setText(tr(self._ui_language, "background"))
        self.output_label.setText(tr(self._ui_language, "save_as"))
        placeholder_key = "audio_output_name_placeholder" if audio_mode else "video_output_name_placeholder"
        self.output_edit.setPlaceholderText(tr(self._ui_language, placeholder_key))
        self._refresh_output_button_tooltip()
        self.format_combo.setToolTip("")
        self.quality_combo.setToolTip("")

    def _combo_changed(self) -> None:
        self._capture_current_values()
        self._refresh_profile_hint()
        self._refresh_image_button()
        self.preferences_changed.emit()

    def _capture_current_values(self) -> None:
        if self._conversion_mode == MODE_VIDEO_TO_AUDIO:
            audio_format = self.format_combo.currentData()
            audio_profile = self.quality_combo.currentData()
            if audio_format is not None:
                self._audio_format = str(audio_format)
            if audio_profile is not None:
                self._audio_profile = str(audio_profile)
        else:
            aspect_ratio = self.format_combo.currentData()
            quality = self.quality_combo.currentData()
            background_mode = self.background_combo.currentData()
            if aspect_ratio is not None:
                self._aspect_ratio = str(aspect_ratio)
            if quality is not None:
                self._quality = str(quality)
            if background_mode is not None:
                self._background_mode = str(background_mode)

    def _refresh_profile_hint(self) -> None:
        if self._conversion_mode != MODE_VIDEO_TO_AUDIO:
            self.profile_hint.clear()
            return
        keys = {
            "Voz": "audio_profile_hint_voice",
            "Estándar": "audio_profile_hint_standard",
            "Original": "audio_profile_hint_original",
        }
        self.profile_hint.setText(tr(self._ui_language, keys.get(self.selected_audio_profile(), "audio_profile_hint_voice")))

    def _select_background_image(self) -> None:
        patterns = " ".join(f"*{extension}" for extension in sorted(SUPPORTED_IMAGE_EXTENSIONS))
        selected, _ = QFileDialog.getOpenFileName(
            self,
            tr(self._ui_language, "select_image_dialog"),
            self._background_image,
            f"{tr(self._ui_language, 'image_filter')} ({patterns})",
        )
        if selected:
            self._background_image = selected
            self._refresh_image_button()
            self.preferences_changed.emit()

    def _browse_output(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            tr(self._ui_language, "select_output_folder"),
            self.output_dir(),
        )
        if selected:
            self._output_dir = selected
            self._refresh_output_button_tooltip()
            self.preferences_changed.emit()

    def _refresh_output_button_tooltip(self) -> None:
        self.output_button.setToolTip(f"{tr(self._ui_language, 'select_output_folder')}\n{self.output_dir()}")

    def _refresh_image_button(self) -> None:
        is_image = self._conversion_mode == MODE_AUDIO_TO_VIDEO and self.selected_background() == "Imagen"
        self.image_button.setVisible(is_image)
        self.image_button.setEnabled(is_image)
        if self._background_image:
            self.image_button.setText(tr(self._ui_language, "image_selected"))
            self.image_button.setToolTip(self._background_image)
        else:
            self.image_button.setText(tr(self._ui_language, "choose_image"))
            self.image_button.setToolTip(tr(self._ui_language, "image_not_selected"))

    def _default_dir_for_mode(self, conversion_mode: str) -> str:
        if conversion_mode == MODE_VIDEO_TO_AUDIO:
            return str(AppPaths.audios_dir())
        return str(AppPaths.videos_dir())

    def _select_data(self, combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)
