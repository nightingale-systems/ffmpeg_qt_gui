import json
import subprocess
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from ui.file_drop import FileDropWidget
from ffmpeg.builder import build_command
from ffmpeg.runner import FFmpegRunner
from models.job import Job, JobState

import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FFmpeg GUI")
        self.resize(900, 500)

        central = QWidget()
        main = QVBoxLayout(central)
        main.setSpacing(12)

        # Drop area (dominant)
        self.drop = FileDropWidget()
        self.drop.fileDropped.connect(self.on_file)

        # Controls row
        controls = QHBoxLayout()

        self.format_box = QComboBox()
        self.format_box.addItems(["mp4", "mkv", "webm", "mp3", "wav", "aac"])

        self.start_btn = QPushButton("Start")
        self.start_btn.setMinimumWidth(120)
        self.start_btn.clicked.connect(self.start_ffmpeg)

        controls.addWidget(QLabel("Format:"))
        controls.addWidget(self.format_box)
        controls.addStretch()
        controls.addWidget(self.start_btn)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        # Layout assembly
        main.addWidget(self.drop, stretch=3)
        main.addLayout(controls, stretch=0)
        main.addWidget(self.progress, stretch=0)

        # ffmpeg log panel 
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setMinimumHeight(150)
        main.addWidget(self.log_panel, stretch=1)

        self.jobs = []
        self.current_job_index = -1

        self.setCentralWidget(central)
    

        self.input_path = None

    def on_file(self, dropped):
        # dropped comes from the signal (str or list of QUrls)
        paths = []

        if isinstance(dropped, str):
            if dropped == "__browse__":
                # open file dialog for multiple selection
                paths, _ = QFileDialog.getOpenFileNames(self, "Select input files")
            else:
                paths = [dropped]
        elif isinstance(dropped, list):
            # convert QUrls to local paths
            for url in dropped:
                paths.append(url.toLocalFile())

        if not paths:
            return

        # Add files to the job queue
        self.add_jobs(paths)

    def start_ffmpeg(self):
        if not self.input_path or not os.path.exists(self.input_path):
            QMessageBox.warning(self, "Error", "No valid input file")
            return

        fmt = self.format_box.currentText()
        cmd, _ = build_command(self.input_path, fmt)

        self.start_btn.setEnabled(False)
        self.progress.setValue(0)
        duration = get_duration(self.input_path)

        self.runner = FFmpegRunner(cmd, duration=duration)
        self.runner.progress.connect(
            lambda p: self.progress.setValue(int(p * 100))
        )
        self.runner.log.connect(self.append_log)
        self.runner.finished.connect(self.on_finished)
        self.runner.start()
        
    def on_finished(self, code):
        self.start_btn.setEnabled(True)
        QMessageBox.information(self, "Done", "FFmpeg finished")

    def add_jobs(self, paths):
        for p in paths:
            self.jobs.append(Job(p, self.format_box.currentText()))
        if self.current_job_index == -1:
            self.start_next_job()

    def start_next_job(self):
        self.current_job_index += 1
        if self.current_job_index >= len(self.jobs):
            self.current_job_index = -1
            return
        job = self.jobs[self.current_job_index]
        job.state = JobState.RUNNING

        cmd, _ = build_command(job.input_path, job.output_format)
        duration = get_duration(job.input_path)
        self.runner = FFmpegRunner(cmd, duration=duration)
        self.runner.progress.connect(lambda p: self.progress.setValue(int(p*100)))
        self.runner.log.connect(self.append_log)
        self.runner.finished.connect(self.on_job_finished)
        self.runner.start()

    def on_job_finished(self, code):
        job = self.jobs[self.current_job_index]
        job.state = JobState.DONE if code == 0 else JobState.ERROR
        self.start_next_job()

    def append_log(self, text):
        self.log_panel.append(text)
        self.log_panel.verticalScrollBar().setValue(
            self.log_panel.verticalScrollBar().maximum()
        )
def get_duration(path: str) -> float | None:
    """
    Returns video duration in seconds using ffprobe, or None if failed.
    """
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration", "-of", "json", path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except Exception:
        return None