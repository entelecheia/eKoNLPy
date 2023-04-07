"""
test cli module
"""
import subprocess
from typing import List, Tuple


def capture(command: List[str]) -> Tuple[bytes, bytes, int]:
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_cli() -> None:
    """Test cli module"""
    command = ["ekonlpy"]
    out, err, exitcode = capture(command)
    assert exitcode == 0
