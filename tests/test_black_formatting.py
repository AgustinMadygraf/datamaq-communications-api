from pathlib import Path
import subprocess
import sys


def test_black_check_passes() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", "."],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Black formatting check failed.\n" f"stdout:\n{result.stdout}\n" f"stderr:\n{result.stderr}"
    )
