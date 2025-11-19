USE_PER_TAB_PROJECT_HISTORY=1

# Wait for ITERM_SESSION_ID to be available (with timeout)
waitForSessionId() {
    local max_attempts=10
    local attempt=0
    while [[ -z "$ITERM_SESSION_ID" && $attempt -lt $max_attempts ]]; do
        sleep 0.1
        attempt=$((attempt + 1))
    done
    if [[ -z "$ITERM_SESSION_ID" ]]; then
        echo "Warning: ITERM_SESSION_ID not available after waiting" >&2
        return 1
    fi
    return 0
}

setupHistory () {
    # Save current history before switching (failsafe against history loss)
    if [ ${SHELL##*/} = "zsh" ] && [ -n "$HISTFILE" ] && [ -f "$HISTFILE" ]; then
        # Try to write history, but don't fail if fc -W isn't available
        fc -W 2>/dev/null || true  # Write current history to disk
    fi
    
    # Wait for ITERM_SESSION_ID if we're using per-tab history and it's not set
    if [[ $USE_PER_TAB_PROJECT_HISTORY = 1 ]] && [[ -z "$ITERM_SESSION_ID" ]]; then
        waitForSessionId
    fi
    
    # Example ITERM_SESSION_ID: w0t1p0:4485B3A5-0ED3-4672-83A1-4010F0B9373E
    if [[ -n $ITERM_SESSION_ID ]]; then
        T=$(echo $ITERM_SESSION_ID| cut -d':' -f 1)
        W=$(echo ${T:1}| cut -d't' -f 1)
        R=t$(echo ${T:1}| cut -d't' -f 2)
    else
        # Fallback if no ITERM_SESSION_ID
        T="w0t0p0"
        W="0"
        R="t0p0"
    fi
    if [ -z "${PROJECT_WINDOW_NUM+1}" ] ; then
        W=0
    else
        W=$PROJECT_WINDOW_NUM
    fi
    if [[ $USE_PER_TAB_PROJECT_HISTORY = 1 ]] ; then
        # Use actual session ID for unique file naming
        if [[ -n $PROJECT_NAME ]] ; then
            D=${HOME}/.history/project/${PROJECT_NAME}
            mkdir -p ${D}
            # Use the full session ID part for uniqueness across tabs
            # CRITICAL FIX: Check if ITERM_SESSION_ID is set before using it
            if [[ -n $ITERM_SESSION_ID ]]; then
                SESSION_PART=$(echo $ITERM_SESSION_ID| cut -d':' -f 1)
                NEWHISTFILE="${D}/${ITERM_PROFILE}.${SESSION_PART}.history"
            else
                # Fallback: use timestamp + random to avoid collisions
                SESSION_PART="w0t$(date +%s)_$$"
                NEWHISTFILE="${D}/${ITERM_PROFILE}.${SESSION_PART}.history"
            fi
        elif [[ -n $ITERM_SESSION_ID ]] ; then
            D=${HOME}/.history/profiles/${ITERM_PROFILE}
            mkdir -p ${D}
            SESSION_PART=$(echo $ITERM_SESSION_ID| cut -d':' -f 1)
            NEWHISTFILE="${D}/${ITERM_PROFILE}.${SESSION_PART}.history"
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

    # Ensure NEWHISTFILE is set
    if [[ -z "$NEWHISTFILE" ]]; then
        echo "Error: Could not determine history file location" >&2
        return 1
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
        
        # Load existing history from the new file
        if [[ -f "$HISTFILE" ]]; then
            history -r "$HISTFILE"
        fi
    elif [ ${SHELL##*/} = "zsh" ]; then
        # Set history file and size variables BEFORE configuring options
        export HISTSIZE=100000
        export SAVEHIST=100000
        
        # Configure zsh history options BEFORE switching files
        # This ensures INC_APPEND_HISTORY is set before we switch
        unsetopt SHARE_HISTORY      # don't share history between sessions
        setopt INC_APPEND_HISTORY   # append history immediately after each command
        setopt HIST_IGNORE_DUPS     # no consecutive duplications
        setopt HIST_IGNORE_ALL_DUPS # remove older duplicate entries
        setopt HIST_FIND_NO_DUPS    # don't show duplicates in history search
        setopt HIST_NO_STORE        # don't store "history" commands
        setopt HIST_IGNORE_SPACE    # don't store commands prefixed with space
        setopt HIST_REDUCE_BLANKS   # remove extra whitespace from commands
        setopt HIST_SAVE_NO_DUPS    # don't save duplicate entries to history file
        
        # Use fc -p to switch history file (this preserves in-memory history)
        # fc -p loads existing history from the file if it exists
        fc -p $HISTFILE $HISTSIZE $SAVEHIST
        
        # Force immediate write to ensure any pending history is saved
        # With INC_APPEND_HISTORY, history is written automatically, but this ensures it
        fc -W 2>/dev/null || true
    fi
}

# Add exit hook for zsh to save history when shell exits
if [ ${SHELL##*/} = "zsh" ]; then
    zshexit() {
        # Save history when shell exits
        if [[ -n "$HISTFILE" ]]; then
            # Try to write history, but don't fail if fc -W isn't available
            fc -W 2>/dev/null || true
        fi
    }
fi
