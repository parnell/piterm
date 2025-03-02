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
    local curcontext="$curcontext" state line
    typeset -A opt_args

    local cur="${words[CURRENT]}"
    local projects_dir="$P_ITERM_PROJECTS_DIR"
    local -a projects

    # Function to process a directory and add its projects
    _process_directory() {
        local dir="$1"
        local rel_path="${dir#$projects_dir/}"
        
        # Add .sh files in this directory (without the .sh extension)
        for file in "$dir"/*.sh(N); do
            if [[ -f "$file" ]]; then
                local name=${file#$projects_dir/}
                name=${name%.sh}
                projects+=("$name")
            fi
        done
        
        # Process subdirectories
        for subdir in "$dir"/*(/N); do
            if [[ -d "$subdir" ]]; then
                # Add the directory itself with a trailing slash
                local subdir_rel="${subdir#$projects_dir/}"
                projects+=("$subdir_rel/")
                
                # Process the subdirectory recursively
                _process_directory "$subdir"
            fi
        done
    }
    
    # Start processing from the projects directory
    _process_directory "$projects_dir"

    # Complete the projects
    _describe -t projects 'projects' projects
}

# Bind the function to the restore_project command
compdef _complete_projects restore_project