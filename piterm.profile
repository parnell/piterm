# Expand path
PATH="$PATH:$HOME/.piterm/bin"

export P_ITERM_HOME="${HOME}/.piterm"
export P_ITERM_TEMPLATES="${P_ITERM_HOME}/templates"
export P_ITERM_PROJECTS_DIR="${P_ITERM_PROJECTS_DIR:-${P_ITERM_HOME}/projects}"
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
            local target_dir="$projects_dir"
            local prefix=""
            
            # If word contains a slash, we're completing inside a subdirectory
            if [[ "$word" == */* ]]; then
                local dir_part="${word%/*}"
                target_dir="$projects_dir/$dir_part"
                prefix="$dir_part/"
            fi
            
            if [[ -d "$target_dir" ]]; then
                _tags directories projects
                
                # Handle directories
                if _requested directories; then
                    _path_files -W "$target_dir" -/ -q -P "$prefix"
                fi
                
                # Handle .sh files (projects)
                if _requested projects; then
                    local -a project_files=()
                    for file in "$target_dir"/*.sh(N); do
                        local basename=${file:t:r}
                        # Skip if there's a directory with the same name
                        [[ ! -d "$target_dir/$basename" ]] && project_files+=("$basename")
                    done
                    
                    [[ ${#project_files} -gt 0 ]] && compadd -q -P "$prefix" -o nosort -X "Projects" -a project_files
                fi
            fi
            ;;
    esac
}

# Bind the function to the restore_project command and its alias
compdef _restore_project restore_project
compdef _restore_project rproj