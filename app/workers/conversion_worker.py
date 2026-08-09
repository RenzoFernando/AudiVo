from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from app.application.conversion_service import ConversionCancelled, ConversionService
from app.domain.conversion_request import ConversionRequest


class ConversionWorker(QObject):
    progress = Signal(int)
    status = Signal(str)
    completed = Signal(str)
    failed = Signal(str)
    cancelled = Signal()
    finished = Signal()

    def __init__(self, request: ConversionRequest) -> None:
        super().__init__()
        self._request = request
        self._cancel_event = threading.Event()
        self._service = ConversionService()

    @Slot()
    def run(self) -> None:
        try:
            output = self._service.convert(
                self._request,
                self._cancel_event,
                self.progress.emit,
                self.status.emit,
            )
            if self._cancel_event.is_set():
                self.cancelled.emit()
            else:
                self.completed.emit(str(output))
        except ConversionCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()

    def request_cancel(self) -> None:
        self._cancel_event.set()
        self._service.cancel()
