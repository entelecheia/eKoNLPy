import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(os.name == "nt" or not shutil.which("make") or not shutil.which("bash"), reason="POSIX Make gate")
@pytest.mark.parametrize("pytest_exit", [0, 17])
def test_make_test_preserves_pytest_exit_status(tmp_path, pytest_exit):
    # Substitute the pytest launcher, retaining the real Make recipe and tee.
    launcher = tmp_path / "uv"
    launcher.write_text(f"#!/usr/bin/env bash\necho 'pytest gate probe'\nexit {pytest_exit}\n", encoding="utf-8")
    launcher.chmod(0o755)
    (tmp_path / "tests").mkdir()
    env = os.environ.copy()
    env["PATH"] = str(tmp_path) + os.pathsep + env["PATH"]
    makefile = Path(__file__).resolve().parents[2] / "Makefile"
    result = subprocess.run(
        [shutil.which("make"), "-f", str(makefile), "test"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) == (pytest_exit == 0)
    assert (tmp_path / "tests" / "pytest-coverage.txt").read_text(encoding="utf-8") == "pytest gate probe\n"
