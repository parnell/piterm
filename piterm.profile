#expand path
PATH="$HOME/.piterm/bin:$PATH"

export P_ITERM_HOME="${HOME}/.piterm"
export P_ITERM_TEMPLATES="${P_ITERM_HOME}/templates"
export P_ITERM_PROJECTS_DIR="${P_ITERM_HOME}/projects"
export P_ITERM_WORKSPACE_DIR="${HOME}/workspace"

source "${P_ITERM_HOME}/advanced_history.profile"

alias rproj=restore_project
alias lproj=list_projects
alias nproj=new_project

### tab completion for projects
autoload -U +X compinit && compinit
autoload -U +X bashcompinit && bashcompinit

_compprojs() {
	cd $P_ITERM_PROJECTS_DIR
    cur=${COMP_WORDS[COMP_CWORD]}
	ar=( $(compgen -f $P_ITERM_PROJECTS_DIR/$cur ) )
	COMPREPLY=()
	for c in ${ar[@]} ; do
		if [[ -d $c ]] ; then 
			COMPREPLY+=("$c/")
		else
			COMPREPLY+=("$c")
		fi
	done
	COMPREPLY=("${COMPREPLY[@]%.*}")
    return 0
}

complete -F _compprojs -o nospace restore_project
complete -F _compprojs new_project

fix_project(){
	local proj=$1
	# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
	# echo $SCRIPT_DIR "-" ${BASH_SOURCE[0]}
	# while true; do
	# 	echo -n 'Attempt to fix this project script? [Yn]:'
	# 	read yn
	# 	case $yn in
			# [Yy]* ) 
				## Find path locations and check to make sure there aren't multiple projects
				local script_loc=$(echo $funcstack | tr -s ' ' | cut -d" " -f2-)
				local proj_loc=$(find ~/workspace -type d -name $proj)
				local c=$(echo $proj_loc | grep -c $proj)
				echo "is $script_loc - $c - $proj_loc"
				if [[ $c -eq 1 ]] ; then 
					local n_proj=$(printf '%s\n' "$script_loc" | sed -e 's/[\/&]/\\&/g')
					echo "n = $n_proj"
					cat $script_loc | sed -e "s/^D=.*/D=$n_proj/"
				else 
					echo "not 1"
				fi
				echo "done"
	# 			break;;
	# 		* ) break;;
	# 	esac
	# done
}
