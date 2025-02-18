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

# Define the autocomplete function
_complete_projects() {
    # Ensure the environment variable is set
    if [[ -z "$P_ITERM_PROJECTS_DIR" ]]; then
        return 1
    fi

    # Get the current word being completed
    local cur_word
    cur_word="${words[CURRENT]}"

    # Use the find command to list all .sh project files and directories
    local project_files directories
    project_files=$(find "$P_ITERM_PROJECTS_DIR" -type f -name '*.sh' ! -path "$P_ITERM_PROJECTS_DIR" -print 2>/dev/null)
    directories=$(find "$P_ITERM_PROJECTS_DIR" -type d ! -path "$P_ITERM_PROJECTS_DIR" -print 2>/dev/null)

    # Extract the project names from the full paths
    local file_names dir_names
    file_names=()
    dir_names=()
    for project in ${(f)project_files}; do
        project_name="${project#$P_ITERM_PROJECTS_DIR/}"
		if [[ $project_name != ".sh" ]]; then
        	file_names+=("${project_name%.sh}")
		fi
    done
    for dir in ${(f)directories}; do
        dir_name="${dir#$P_ITERM_PROJECTS_DIR/}"
        dir_names+=("$dir_name")
    done

    # Filter out nested files and directories unless the parent path is typed
    if [[ "$cur_word" == */* ]]; then
        file_names=("${(@)file_names:#${cur_word}/*}")
        dir_names=("${(@)dir_names:#${cur_word}/*/}")
    else
        file_names=("${(@)file_names:#*/*}")
        dir_names=("${(@)dir_names:#*/*}/")
    fi


    _alternative \
        'project-files:projects:(${file_names[@]})' \
        'directories:dirs:(${dir_names[@]})'
}

# Bind the function to the restore_project command
compdef _complete_projects restore_project