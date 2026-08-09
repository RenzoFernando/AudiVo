from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout

from app.presentation.translations import tr


class ProgressWidget(QFrame):
    def __init__(self, ui_language: str = "es", parent=None) -> None:
        super().__init__(parent)
        self._ui_language = ui_language
        self._waiting_step = 1
        self._waiting_active = True
        self.setObjectName("progressFrame")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(5)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel()
        self.status_label.setObjectName("progressStatusLabel")
        self.status_label.setProperty("state", "idle")
        self.detail_label = QLabel("")
        self.detail_label.setObjectName("etaLabel")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.status_label, 1)
        header.addWidget(self.detail_label)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addLayout(header)
        layout.addWidget(self.progress)
        self._waiting_timer = QTimer(self)
        self._waiting_timer.setInterval(500)
        self._waiting_timer.timeout.connect(self._advance_waiting_animation)
        self._update_waiting_text()
        self._waiting_timer.start()

    def set_ui_language(self, ui_language: str) -> None:
        self._ui_language = ui_language
        if self._waiting_active:
            self._update_waiting_text()

    def set_waiting(self) -> None:
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.detail_label.setText("")
        self._start_waiting_animation()
        self._set_state("idle")

    def set_ready(self) -> None:
        self._stop_waiting_animation()
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label.setText(tr(self._ui_language, "ready"))
        self.detail_label.setText("")
        self._set_state("idle")

    def set_processing(self, value: int = 0, detail: str = "") -> None:
        self._stop_waiting_animation()
        normalized = max(0, min(100, int(value)))
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(normalized)
        self.status_label.setText(tr(self._ui_language, "status_creating_video", value=normalized))
        self.detail_label.setText(detail)
        self._set_state("idle")

    def set_completed(self) -> None:
        self._stop_waiting_animation()
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.status_label.setText(tr(self._ui_language, "status_completed_percent"))
        self.detail_label.setText(tr(self._ui_language, "finished"))
        self._set_state("completed")

    def set_cancelled(self) -> None:
        self._stop_waiting_animation()
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label.setText(tr(self._ui_language, "status_cancelled"))
        self.detail_label.setText(tr(self._ui_language, "partial_removed"))
        self._set_state("idle")

    def set_error(self) -> None:
        self._stop_waiting_animation()
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label.setText(tr(self._ui_language, "conversion_error_status"))
        self.detail_label.setText("")
        self._set_state("idle")

    def _start_waiting_animation(self) -> None:
        self._waiting_active = True
        self._waiting_step = 1
        self._update_waiting_text()
        if not self._waiting_timer.isActive():
            self._waiting_timer.start()

    def _stop_waiting_animation(self) -> None:
        self._waiting_active = False
        self._waiting_timer.stop()

    def _advance_waiting_animation(self) -> None:
        if not self._waiting_active:
            return
        self._waiting_step = 1 if self._waiting_step >= 3 else self._waiting_step + 1
        self._update_waiting_text()

    def _update_waiting_text(self) -> None:
        self.status_label.setText(f"{tr(self._ui_language, 'status_waiting')}{'.' * self._waiting_step}")

    def _set_state(self, state: str) -> None:
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
