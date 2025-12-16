import os

def build_command(input_path: str, fmt: str) -> tuple[list[str], str]:
    base, _ = os.path.splitext(input_path)
    output = f"{base}.{fmt}"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        output
    ]
    return cmd, output
