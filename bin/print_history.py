import os
import sys
from datetime import datetime
from collections import defaultdict
import glob

def getLine(line, prev):
    if line.strip().startswith(': '): # zsh history
        s = line.strip().split(':')
        etime = datetime.fromtimestamp(int(s[1].strip()))
        rtime, cmd = s[2].split(';',1)
        return cmd+'\n', etime, rtime, False
    elif prev.rstrip().endswith('\\'):
        return line, None, None, True
    else:
        raise Exception("Bash not currently supported")

def print_history(pname, iterm_profile):
    if pname:
        D='{}/.history/project/{}'.format(home, pname)
    elif iterm_profile:
        D='{}/.history/profiles/{}'.format(home, iterm_profile)
    else:
        D='{}/.history'.format(home)

    cmds = defaultdict(list)
    count = 0
    for filename in glob.iglob('{}/*.history'.format(D), recursive=True):
        prev = None
        petime = None
        for line in open(filename):
            cmd, etime, rtime, continuation = getLine(line, prev)
            if continuation:
                cmds[petime][-1] = (cmds[petime][-1][0]+cmd, cmds[petime][-1][1])
                continue
            cmds[etime].append((cmd, rtime))
            prev = line
            petime = etime
            count+=1


    # example hist
    #    1  2018-11-21 15:19:43  history
    i = 1
    l = max(5,len(str(count)))
    fstr = "{:%d}  {}\t{}"%l
    for kt in sorted(cmds.keys()):
        cmdpair_list = cmds[kt]
        for cmd, rtime in cmdpair_list:
            print(fstr.format(i,kt, cmd.rstrip()))
            i+=1

if __name__ == "__main__":
    home = os.environ.get('HOME')
    pname = os.environ.get('PROJECT_NAME')
    profile = os.environ.get('ITERM_PROFILE')
    if len(sys.argv) == 3:
        pname = sys.argv[1]
        profile = sys.argv[2]

    print_history(pname, profile)
