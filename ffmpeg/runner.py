# ffmpeg/ffmpeg_runner.pyfrom PySide6.QtCore 
from PySide6.QtCore import QObject, QProcess, Signal
import re

class FFmpegRunner(QObject):
    progress = Signal(float)
    log = Signal(str)
    finished = Signal(int)

    def __init__(self, cmd: list[str], duration: float | None = None):
        super().__init__()
        self.cmd = cmd
        self.duration = duration
        self.proc = QProcess()
        self.proc.readyReadStandardError.connect(self._read)
        self.proc.finished.connect(self.finished)

    def start(self):
        self.proc.start(self.cmd[0], self.cmd[1:])

    def _read(self):
        text = self.proc.readAllStandardError().data().decode(errors="ignore")
        self.log.emit(text)

        if self.duration:
            m = re.search(r"time=(\d+:\d+:\d+\.\d+)", text)
            if m:
                self.progress.emit(self._to_sec(m.group(1)) / self.duration)

    def _to_sec(self, t):
        h, m, s = t.split(":")
        return int(h)*3600 + int(m)*60 + float(s)
