#!/usr/bin/env python3
import argparse
import glob
import os
import re
import sys
from datetime import datetime
from enum import Enum
from itertools import chain
from typing import Iterator, List, Optional, Tuple


class HistoryType(Enum):
    unknown = 0
    bash = 1
    zsh = 2


class bcolors:
    HEADER: str = "\033[95m"
    BLUE: str = "\033[94m"
    CYAN: str = "\033[96m"
    GREEN: str = "\033[92m"
    ORANGE: str = "\033[93m"
    FAIL: str = "\033[91m"
    ENDC: str = "\033[0m"
    BOLD: str = "\033[1m"
    UNDERLINE: str = "\033[4m"


class Command:
    def __init__(self) -> None:
        self.etime: datetime = datetime.now()  ## Start time
        self.rtime: str = ""  ## Run time
        self.cmd: str = ""  ## Command
        self.type: HistoryType = HistoryType.unknown


# zsh writes a newline inside a history entry as a trailing odd backslash.
# Pairs of trailing backslashes are a literal backslash.
_ZSH_ENTRY = re.compile(r"\A: (\d+):(\d+);(.*)\Z", re.DOTALL)
_BASH_TIMESTAMP = re.compile(r"\A# (\d+)\Z")


def _decode_physical_line(line: str) -> Tuple[str, bool]:
    line = line.rstrip("\r\n")
    trailing = 0
    end = len(line)
    while end > 0 and line[end - 1] == "\\":
        trailing += 1
        end -= 1
    body = line[:end] + ("\\" * (trailing // 2))
    if trailing % 2 == 1:
        return body + "\n", True
    return body, False


def parse_history_file(filename: str) -> List[Command]:
    """Parse a bash or zsh history file in the order the shell loads it."""
    entries: List[str] = []
    pending_text = ""
    with open(filename, encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            text, continues = _decode_physical_line(raw_line)
            pending_text += text
            if continues:
                continue
            if pending_text != "":
                entries.append(pending_text)
            pending_text = ""
        if pending_text:
            entries.append(pending_text)

    commands: List[Command] = []
    pending_bash: Optional[Command] = None
    for entry in entries:
        zsh_match = _ZSH_ENTRY.match(entry)
        bash_match = _BASH_TIMESTAMP.match(entry)
        if zsh_match:
            if pending_bash is not None:
                commands.append(pending_bash)
                pending_bash = None
            command = Command()
            command.etime = datetime.fromtimestamp(int(zsh_match.group(1)))
            command.rtime = zsh_match.group(2)
            command.cmd = zsh_match.group(3)
            command.type = HistoryType.zsh
            commands.append(command)
        elif bash_match:
            if pending_bash is not None:
                commands.append(pending_bash)
            pending_bash = Command()
            pending_bash.etime = datetime.fromtimestamp(int(bash_match.group(1)))
            pending_bash.type = HistoryType.bash
            pending_bash.cmd = ""
        elif pending_bash is not None:
            if pending_bash.cmd:
                pending_bash.cmd += "\n" + entry
            else:
                pending_bash.cmd = entry
    if pending_bash is not None:
        commands.append(pending_bash)
    return commands


def print_history(
    pname: Optional[str] = None,
    iterm_profile: Optional[str] = None,
    all_history: Optional[bool] = None,
    histfile: Optional[str] = None,
    show_filenames: bool = False,
    color: bool = False,
    ignore_errors: bool = False,
) -> None:
    if histfile:
        # Single file mode for tab history
        files: Iterator[str] = iter([os.path.expanduser(histfile)])
    elif all_history:
        files = chain(
            glob.iglob(os.path.expanduser("~/.zsh_history")),
            glob.iglob(os.path.expanduser("~/.bash_history")),
            glob.iglob(os.path.expanduser("~/.history/**"), recursive=True),
        )
    elif pname:
        files = glob.iglob(
            os.path.expanduser(f"~/.history/project/{pname}/*"), recursive=False
        )
    elif iterm_profile:
        files = glob.iglob(
            os.path.expanduser(f"~/.history/profiles/{iterm_profile}"), recursive=True
        )
    else:
        files = chain(
            glob.iglob(os.path.expanduser("~/.zsh_history")),
            glob.iglob(os.path.expanduser("~/.bash_history")),
            glob.iglob(os.path.expanduser("~/.history/**"), recursive=True),
        )

    # Tab history follows the file, which is the order Up walks.
    # Merged views sort each file by timestamp.
    preserve_order = histfile is not None
    for filename in files:
        if os.path.isdir(filename):
            continue
        try:
            commands = parse_history_file(filename)
        except Exception as e:
            print(f"Parse Error '{filename}': \n{str(e)}", file=sys.stderr)
            if not ignore_errors:
                raise
            commands = []
        if not preserve_order:
            commands = sorted(commands, key=lambda command: command.etime)
        if show_filenames:
            try:
                if color:
                    print(f"{bcolors.GREEN}{filename}{bcolors.ENDC}")
                else:
                    print(filename)
            except BrokenPipeError:
                sys.exit(0)

        # example hist
        #    1  2018-11-21 15:19:43  history
        width: int = max(5, len(str(len(commands))))
        fstr: str = "{:%d}  {}\t{}" % width
        for i, command in enumerate(commands, start=1):
            try:
                print(fstr.format(i, command.etime, command.cmd.rstrip()))
            except BrokenPipeError:
                sys.exit(0)
            except Exception:
                print("error on line", i, command)


if __name__ == "__main__":
    ## Only color if we are going to terminal
    use_color: bool = True if sys.stdout.isatty() else False

    parser = argparse.ArgumentParser(description="print shell history")
    parser.add_argument("--all-history", action="store_true", help="show all history")
    parser.add_argument("--show-filenames", action="store_true", help="show filenames")
    parser.add_argument("--project-name", help="specify a project name")
    parser.add_argument("--iterm-profile", help="specify the profile")
    parser.add_argument("--histfile", help="specify a specific history file to read")
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="ignore certain errors while printing history",
    )
    parser.add_argument(
        "--force-color", action="store_true", help="force color even in piped output"
    )
    parser.add_argument(
        "--fc", action="store_true", help="force color even in piped output"
    )

    args = parser.parse_args()

    try:
        print_history(
            args.project_name,
            args.iterm_profile,
            all_history=args.all_history,
            histfile=args.histfile,
            show_filenames=args.show_filenames,
            color=args.force_color or args.fc or use_color,
            ignore_errors=args.ignore_errors,
        )
    except BrokenPipeError:
        # Broken pipe is normal when piping to commands that exit early (e.g., grep with errors)
        sys.exit(0)
