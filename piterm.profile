# Expand path
PATH="$PATH:$HOME/.piterm/bin"

export P_ITERM_HOME="${HOME}/.piterm"
export P_ITERM_TEMPLATES="${P_ITERM_HOME}/templates"
export P_ITERM_PROJECTS_DIR="${P_ITERM_HOME}/projects"
export P_ITERM_WORKSPACE_DIR="${HOME}/workspace"

source "${P_ITERM_HOME}/advanced_history.profile"

alias rproj=restore_project
alias lproj=list_projects
alias nproj=new_project

# Enable menu selection for better navigation
zstyle ':completion:*:restore_project:*' menu select
# Enable partial word completion
zstyle ':completion:*:restore_project:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'
# Use terminal's LS_COLORS for coloring
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
# Ensure restore_project specifically uses colors
zstyle ':completion:*:restore_project:*' list-colors ${(s.:.)LS_COLORS}

# Define the autocomplete function
_restore_project() {
    local curcontext="$curcontext" state line
    typeset -A opt_args
    
    _arguments -C \
        '1:project:->projects' \
        '*::arg:->args'
    
    case $state in
        projects)
            local projects_dir="$P_ITERM_PROJECTS_DIR"
            local word="$words[CURRENT]"
            
            # If word contains a slash, we're completing inside a directory
            if [[ "$word" == */* ]]; then
                local dir_part="${word%/*}"
                local target_dir="$projects_dir/$dir_part"
                
                if [[ -d "$target_dir" ]]; then
                    # Complete files and directories in the target directory
                    _files -W "$target_dir" -g "*.sh(:r)" -P "$dir_part/"
                    _files -W "$target_dir" -/ -P "$dir_part/"
                fi
            else
                # Top level completion
                _files -W "$projects_dir" -g "*.sh(:r)"
                _files -W "$projects_dir" -/
            fi
            ;;
    esac
}

# Bind the function to the restore_project command
compdef _restore_project restore_project