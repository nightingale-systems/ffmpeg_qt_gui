from dataclasses import dataclass, field
from enum import Enum

class JobState(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    DONE = "Done"
    ERROR = "Error"

@dataclass
class Job:
    input_path: str
    output_format: str
    state: JobState = JobState.PENDING
