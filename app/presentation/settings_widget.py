from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QComboBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QWidget

from app.constants import ASPECT_RATIOS, BACKGROUNDS, QUALITIES, SUPPORTED_IMAGE_EXTENSIONS
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
        ui_language: str = "es",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._ui_language = ui_language
        self._background_image = background_image
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
        self.image_button = QPushButton()
        self.image_button.setObjectName("imageButton")
        self.image_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.image_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.image_button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        self.output_edit = QLineEdit(output_dir)
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
        layout.addWidget(self.background_combo, 3, 0)
        layout.addWidget(self.image_button, 3, 1)
        layout.addWidget(self.output_label, 4, 0, 1, 2)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        output_row = QHBoxLayout()
        output_row.setSpacing(6)
        output_row.addWidget(self.output_edit, 1)
        output_row.addWidget(self.output_button)
        layout.addLayout(output_row, 5, 0, 1, 2)
        self._populate_combos(aspect_ratio, quality, background_mode)
        self.format_combo.currentIndexChanged.connect(self.preferences_changed.emit)
        self.quality_combo.currentIndexChanged.connect(self.preferences_changed.emit)
        self.background_combo.currentIndexChanged.connect(self._background_changed)
        self.image_button.clicked.connect(self._select_background_image)
        self.output_edit.editingFinished.connect(self.preferences_changed.emit)
        self.output_button.clicked.connect(self._browse_output)
        self.set_ui_language(ui_language)
        self._refresh_image_button()

    def selected_aspect_ratio(self) -> str:
        return str(self.format_combo.currentData())

    def selected_quality(self) -> str:
        return str(self.quality_combo.currentData())

    def selected_background(self) -> str:
        return str(self.background_combo.currentData())

    def background_image(self) -> str:
        return self._background_image

    def clear_background_image(self) -> None:
        self._background_image = ""
        self._refresh_image_button()

    def output_dir(self) -> str:
        return self.output_edit.text().strip()

    def set_ui_language(self, ui_language: str) -> None:
        aspect_ratio = self.selected_aspect_ratio()
        quality = self.selected_quality()
        background_mode = self.selected_background()
        self._ui_language = ui_language
        self.format_combo.blockSignals(True)
        self.quality_combo.blockSignals(True)
        self.background_combo.blockSignals(True)
        self._populate_combos(aspect_ratio, quality, background_mode)
        self.format_combo.blockSignals(False)
        self.quality_combo.blockSignals(False)
        self.background_combo.blockSignals(False)
        self.format_label.setText(tr(ui_language, "format"))
        self.quality_label.setText(tr(ui_language, "quality"))
        self.background_label.setText(tr(ui_language, "background"))
        self.output_label.setText(tr(ui_language, "save_in"))
        self.output_button.setToolTip(tr(ui_language, "select_output_folder"))
        self._refresh_image_button()

    def set_interactions_enabled(self, enabled: bool) -> None:
        self.format_combo.setEnabled(enabled)
        self.quality_combo.setEnabled(enabled)
        self.background_combo.setEnabled(enabled)
        self.image_button.setEnabled(enabled and self.selected_background() == "Imagen")
        self.output_edit.setEnabled(enabled)
        self.output_button.setEnabled(enabled)

    def _populate_combos(self, aspect_ratio: str, quality: str, background_mode: str) -> None:
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
        self.format_combo.clear()
        self.quality_combo.clear()
        self.background_combo.clear()
        for value in ASPECT_RATIOS:
            self.format_combo.addItem(aspect_labels.get(value, value), value)
        for value in QUALITIES:
            self.quality_combo.addItem(value, value)
        for value in BACKGROUNDS:
            self.background_combo.addItem(background_labels.get(value, value), value)
        self._select_data(self.format_combo, aspect_ratio)
        self._select_data(self.quality_combo, quality)
        self._select_data(self.background_combo, background_mode)

    def _background_changed(self) -> None:
        self._refresh_image_button()
        self.preferences_changed.emit()

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
            self.output_edit.text(),
        )
        if selected:
            self.output_edit.setText(selected)
            self.preferences_changed.emit()

    def _refresh_image_button(self) -> None:
        is_image = self.selected_background() == "Imagen"
        self.image_button.setVisible(is_image)
        self.image_button.setEnabled(is_image)
        if self._background_image:
            self.image_button.setText(tr(self._ui_language, "image_selected"))
            self.image_button.setToolTip(self._background_image)
        else:
            self.image_button.setText(tr(self._ui_language, "choose_image"))
            self.image_button.setToolTip(tr(self._ui_language, "image_not_selected"))

    def _select_data(self, combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)
