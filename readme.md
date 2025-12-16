ffmpeg-gui/
│
├─ app.py                  # entry point
├─ main_window.py          # QMainWindow
│
├─ ffmpeg/
│   ├─ ffmpeg_runner.py    # runs ffmpeg, parses progress
│   ├─ ffmpeg_presets.py   # preset definitions
│   └─ ffmpeg_builder.py   # turns settings → ffmpeg args
│
├─ models/
│   └─ job.py              # Job dataclass
│   └─ job_queue.py        # queue + state
│
├─ ui/
│   ├─ job_table.py        # QTableView + model
│   └─ preset_editor.py
│
└─ util/
    └─ paths.py


Qt — the right tool

Pros

Mature, boring, reliable. Exactly what you want for a media tool.
Cross-platform by default (Windows, Linux, macOS). Huge upside if you ever care later.
Excellent process + threading support for running FFmpeg, capturing stdout/stderr, progress parsing.
Good model/view widgets for job queues, presets, logs, batch lists.
FFmpeg GUIs already exist in Qt → lots of prior art and patterns.
C++ or Python (PySide/PyQt) depending on how hard you want to go.

Cons

UI won’t look “Windows-native” unless you style it.
Licensing can matter if you ever commercialise (LGPL is fine for most people).

Verdict: Pragmatic, scalable, and frictionless. This is what professionals use when they want something to actually ship.
