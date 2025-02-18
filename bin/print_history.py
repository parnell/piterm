#!/usr/bin/env python3
import os
import sys
import argparse
from itertools import chain
from datetime import datetime
from collections import defaultdict
import glob
from datetime import datetime
from enum import Enum

class HistoryType(Enum):
    unknown=0
    bash=1
    zsh=2


class bcolors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ORANGE = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

class Command():
    def __init__(self):
        self.etime = None ## Start time
        self.rtime = None ## Run time
        self.cmd = None ## Command

def print_history(
    pname=None,
    iterm_profile=None,
    all_history=None,
    show_filenames=False,
    color=False,
    ignore_errors=False,
):
    if all_history:
        files = chain(
            glob.iglob(os.path.expanduser("~/.zsh_history")),
            glob.iglob(os.path.expanduser("~/.bash_history")),
            glob.iglob(os.path.expanduser(f"~/.history/**"), recursive=True),
        )
    elif pname:
        files = glob.iglob(os.path.expanduser(f"~/.history/project/{pname}"), recursive=True)
    elif iterm_profile:
        files = glob.iglob(
            os.path.expanduser(f"~/.history/profiles/{iterm_profile}"), recursive=True
        )
    else:
        files = chain(
            glob.iglob(os.path.expanduser("~/.zsh_history")),
            glob.iglob(os.path.expanduser("~/.bash_history")),
            glob.iglob(os.path.expanduser(f"~/.history/**"), recursive=True),
        )

    fcmds = {}
    count = 0
    for filename in files:
        if os.path.isdir(filename):
            continue
        cmd_continuation = False
        cmds = defaultdict(list)
        fcmds[filename] = cmds
        cur_cmd = None
        try:
            for line in open(filename, encoding="utf-8", errors="replace"):
                if not line.strip():
                    if cur_cmd: ## Some commands end with a newline after a previous line that ends with \
                        cur_cmd.cmd+=line
                        cmds[cur_cmd.etime].append(cur_cmd)
                        cur_cmd = None
                        cmd_continuation = False
                    continue
                # Need a new command
                if cmd_continuation:
                    cur_cmd.cmd += line
                else:
                    if (line.startswith(": ") or line.startswith("# ")): 
                        if cur_cmd:
                            cmds[cur_cmd.etime].append(cur_cmd)
                        cur_cmd = Command()
                        cmd_continuation = False
                    if line.startswith(": "):  # zsh history
                        s = line.strip().split(":", maxsplit=2)
                        etime = datetime.fromtimestamp(int(s[1].strip()))
                        rtime, cmd = s[2].split(";", maxsplit=1)
                        cur_cmd.rtime = rtime
                        cur_cmd.cmd = cmd
                        cur_cmd.etime = etime
                        cur_cmd.type = HistoryType.zsh
                    elif line.startswith("# "):
                        etime = datetime.fromtimestamp(int(line[1:]))
                        cur_cmd.cmd = ""
                        cur_cmd.etime = etime
                        cur_cmd.type = HistoryType.bash
                cmd_continuation = line.rstrip().endswith("\\")

            if cur_cmd:
                cmds[cur_cmd.etime].append(cur_cmd)
        except Exception as e:
            print(f"Parse Error '{filename}': \n{str(e)}", file=sys.stderr)
            raise
        if show_filenames:
            if color:
                print(f"{bcolors.GREEN}{filename}{bcolors.ENDC}")
            else:
                print(filename)

        # example hist
        #    1  2018-11-21 15:19:43  history
        i = 1
        l = max(5, len(str(count)))
        fstr = "{:%d}  {}\t{}" % l
        for kt in sorted(cmds.keys()):
            cmdlist = cmds[kt]
            for cmd in cmdlist:
                try:
                    print(fstr.format(i, kt, cmd.cmd.rstrip()))
                except:
                    print("error on line", i, cmd)
                i += 1


if __name__ == "__main__":
    ## Only color if we are going to terminal
    use_color = True if sys.stdout.isatty() else False

    parser = argparse.ArgumentParser(description="print shell history")
    parser.add_argument("--all-history", action="store_true", help="show all history")
    parser.add_argument("--show-filenames", action="store_true", help="show filenames")
    parser.add_argument("--project-name", help="specify a project name")
    parser.add_argument("--iterm-profile", help="specify the profile")
    parser.add_argument(
        "--ignore-errors", action="store_true", help="ignore certain errors while printing history"
    )
    parser.add_argument(
        "--force-color", action="store_true", help="force color even in piped output"
    )
    parser.add_argument("--fc", action="store_true", help="force color even in piped output")

    args = parser.parse_args()

    print_history(
        args.project_name,
        args.iterm_profile,
        all_history=args.all_history,
        show_filenames=args.show_filenames,
        color=args.force_color,
        ignore_errors=args.ignore_errors,
    )
