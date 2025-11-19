#!/usr/bin/env python3
import argparse
import glob
import os
import sys
from collections import defaultdict
from datetime import datetime
from enum import Enum
from itertools import chain
from typing import DefaultDict, Dict, Iterator, List, Optional


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


def print_history(
    pname: Optional[str] = None,
    iterm_profile: Optional[str] = None,
    all_history: Optional[bool] = None,
    show_filenames: bool = False,
    color: bool = False,
    ignore_errors: bool = False,
) -> None:
    if all_history:
        files: Iterator[str] = chain(
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

    fcmds: Dict[str, DefaultDict[datetime, List[Command]]] = {}
    count: int = 0
    for filename in files:
        if os.path.isdir(filename):
            continue
        cmd_continuation: bool = False
        cmds: DefaultDict[datetime, List[Command]] = defaultdict(list)
        fcmds[filename] = cmds
        cur_cmd: Optional[Command] = None
        try:
            for line in open(filename, encoding="utf-8", errors="replace"):
                if not line.strip():
                    if cur_cmd:  ## Some commands end with a newline after a previous line that ends with \
                        cur_cmd.cmd += line
                        cmds[cur_cmd.etime].append(cur_cmd)
                        cur_cmd = None
                        cmd_continuation = False
                    continue
                # Need a new command
                if cmd_continuation and cur_cmd is not None:
                    cur_cmd.cmd += line
                else:
                    if line.startswith(": ") or line.startswith("# "):
                        if cur_cmd:
                            cmds[cur_cmd.etime].append(cur_cmd)
                        cur_cmd = Command()
                        cmd_continuation = False
                    if line.startswith(": ") and cur_cmd is not None:  # zsh history
                        s: List[str] = line.strip().split(":", maxsplit=2)
                        etime: datetime = datetime.fromtimestamp(int(s[1].strip()))
                        rtime_cmd: List[str] = s[2].split(";", maxsplit=1)
                        rtime, cmd_str = rtime_cmd[0], rtime_cmd[1]
                        cur_cmd.rtime = rtime
                        cur_cmd.cmd = cmd_str
                        cur_cmd.etime = etime
                        cur_cmd.type = HistoryType.zsh
                    elif line.startswith("# ") and cur_cmd is not None:
                        etime = datetime.fromtimestamp(int(line[1:]))
                        cur_cmd.cmd = ""
                        cur_cmd.etime = etime
                        cur_cmd.type = HistoryType.bash
                cmd_continuation = line.rstrip().endswith("\\")

            if cur_cmd:
                cmds[cur_cmd.etime].append(cur_cmd)
        except Exception as e:
            print(f"Parse Error '{filename}': \n{str(e)}", file=sys.stderr)
            if not ignore_errors:
                raise
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
        i: int = 1
        width: int = max(5, len(str(count)))
        fstr: str = "{:%d}  {}\t{}" % width
        for kt in sorted(cmds.keys()):
            cmdlist: List[Command] = cmds[kt]
            for cmd_obj in cmdlist:
                try:
                    print(fstr.format(i, kt, cmd_obj.cmd.rstrip()))
                except BrokenPipeError:
                    sys.exit(0)
                except Exception:
                    print("error on line", i, cmd_obj)
                i += 1


if __name__ == "__main__":
    ## Only color if we are going to terminal
    use_color: bool = True if sys.stdout.isatty() else False

    parser = argparse.ArgumentParser(description="print shell history")
    parser.add_argument("--all-history", action="store_true", help="show all history")
    parser.add_argument("--show-filenames", action="store_true", help="show filenames")
    parser.add_argument("--project-name", help="specify a project name")
    parser.add_argument("--iterm-profile", help="specify the profile")
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
            show_filenames=args.show_filenames,
            color=args.force_color or args.fc or use_color,
            ignore_errors=args.ignore_errors,
        )
    except BrokenPipeError:
        # Broken pipe is normal when piping to commands that exit early (e.g., grep with errors)
        sys.exit(0)
