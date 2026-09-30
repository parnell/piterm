"""The tab history file and the ring Up walks stay the same list."""
import os
import subprocess
from pathlib import Path

import pytest


PROFILE = Path(__file__).resolve().parents[1] / "advanced_history.profile"


def _run_zsh(home: Path, mem1: Path, mem2: Path) -> subprocess.CompletedProcess[str]:
    hist = home / ".history" / "project" / "demo" / "Demo.w0t4p1.history"
    hist.parent.mkdir(parents=True)
    hist.write_text(
        ": 1700000000:0;echo piterm_alpha_cmd\n"
        ": 1700000001:0;echo piterm_beta_cmd\n"
    )
    script = "\n".join(
        [
            "unset HISTFILE",
            "export SHELL=/bin/zsh",
            f"export HOME={_zsh_quote(home)}",
            "export ITERM_SESSION_ID='w3t4p1:DEAD-BEEF'",
            "export PROJECT_NAME=demo",
            "export ITERM_PROFILE=Demo",
            f"source {_zsh_quote(PROFILE)}",
            "setupHistory || exit 1",
            f"fc -l -n > {_zsh_quote(mem1)}",
            "echo piterm_alpha_cmd",
            f"fc -l -n > {_zsh_quote(mem2)}",
            "exit",
            "",
        ]
    )
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["SHELL"] = "/bin/zsh"
    env.pop("HISTFILE", None)
    return subprocess.run(
        ["zsh", "-f", "-i"],
        input=script,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def _zsh_quote(path: Path) -> str:
    return "'" + str(path).replace("'", "'\\''") + "'"


def test_loaded_history_is_not_duplicated_and_repeats_stay_in_place(tmp_path: Path) -> None:
    mem1 = tmp_path / "mem1.txt"
    mem2 = tmp_path / "mem2.txt"
    home = tmp_path / "home"
    result = _run_zsh(home, mem1, mem2)
    assert result.returncode == 0, result.stderr
    first = mem1.read_text()
    second = mem2.read_text()
    hist = (home / ".history" / "project" / "demo" / "Demo.w0t4p1.history").read_text()

    assert first.count("echo piterm_alpha_cmd") == 1
    assert first.count("echo piterm_beta_cmd") == 1
    assert first.index("echo piterm_alpha_cmd") < first.index("echo piterm_beta_cmd")

    assert second.count("echo piterm_alpha_cmd") == 2
    assert second.index("echo piterm_alpha_cmd") < second.index("echo piterm_beta_cmd")

    assert hist.count("echo piterm_alpha_cmd") == 2
    assert hist.count("echo piterm_beta_cmd") == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", __file__]))
