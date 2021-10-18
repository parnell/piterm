USE_PER_TAB_PROJECT_HISTORY=0
setupHistory () {
    # Example ITERM_SESSION_ID: w0t1p0:4485B3A5-0ED3-4672-83A1-4010F0B9373E
    T=$(echo $ITERM_SESSION_ID| cut -d':' -f 1)
    W=$(echo ${T:1}| cut -d't' -f 1)
    R=t$(echo ${T:1}| cut -d't' -f 2)
    if [ -z "${PROJECT_WINDOW_NUM+1}" ] ; then
        W=0
    else
        W=$PROJECT_WINDOW_NUM
    fi
    if [[ $USE_PER_TAB_PROJECT_HISTORY = 1 ]] ; then
        # This should be investigated further
        l=w$W$R
        if [[ -n $PROJECT_NAME ]] ; then
            D=${HOME}/.history/project/${PROJECT_NAME}
            mkdir -p ${D}
            NEWHISTFILE="${D}/${ITERM_PROFILE}.${l}.history"
        elif [[ -n $ITERM_SESSION_ID ]] ; then
            D=${HOME}/.history/profiles/${ITERM_PROFILE}
            mkdir -p ${D}
            NEWHISTFILE="${D}/${ITERM_PROFILE}.history"
        fi
    else
        if [[ -n $PROJECT_NAME ]] ; then
            D=${HOME}/.history/project/${PROJECT_NAME}
            mkdir -p ${D}
            NEWHISTFILE="${D}/${PROJECT_NAME}.history"
        elif [[ -n $ITERM_SESSION_ID ]] ; then
            D=${HOME}/.history/profiles/${ITERM_PROFILE}
            mkdir -p ${D}
            NEWHISTFILE="${D}/${ITERM_PROFILE}.history"
        fi
    fi

    export HISTFILE=$NEWHISTFILE
    if [ ${SHELL##*/} = "bash" ]; then
        ### currently not working
        export SHORTHISTFILE=${HISTFILE##*bash_history.}

        export HISTCONTROL=ignoredups:erasedups # Avoid duplicates

        export HISTSIZE=100000                   # big big history
        export HISTFILESIZE=100000               # big big history

        # When the shell exits, append to the history file instead of overwriting it
        shopt -s histappend

        # After each command, append to the history file and reread it
        # prompt_add "history -a"
        # prompt_add "history -n"
        # prompt_add "history -w"
        # prompt_add "history -c"
        # prompt_add "history -r"
        export PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"
    elif [ ${SHELL##*/} = "zsh" ]; then
        fc -p $HISTFILE ## set new history file
        echo $HISTFILE
        unsetopt SHARE_HISTORY  # don't share history
        setopt INC_APPEND_HISTORY # append history immediately
        setopt HIST_IGNORE_DUPS # no duplications
        setopt HIST_NO_STORE ## Don't story "history" commands
        setopt HIST_IGNORE_SPACE ## Don't store commands prefixed with space
    fi
}
