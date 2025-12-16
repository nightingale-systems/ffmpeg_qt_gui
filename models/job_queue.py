# models/job_queue.py

# TODO parallel jobs, cancellation, retry

from PySide6.QtCore import QObject, Signal
from .job import Job, JobState

class JobQueue(QObject):
    job_updated = Signal()

    def __init__(self):
        super().__init__()
        self.jobs: list[Job] = []
        self.current = None

    def add_job(self, job: Job):
        self.jobs.append(job)
        self.job_updated.emit()

    def next_job(self):
        for job in self.jobs:
            if job.state == JobState.PENDING:
                return job
        return None
