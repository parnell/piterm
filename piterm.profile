#expand path
PATH="$HOME/.piterm/bin:$PATH"
source "$HOME/.piterm/advanced_history.profile"

alias rproj=restore_project
alias lproj=list_projects
alias nproj=new_project


### tab completion for projects
_compprojs (){
	cur=${COMP_WORDS[COMP_CWORD]};
	COMPREPLY=($(compgen -W "$(list_projects) " -- $cur))
}

complete -F _compprojs restore_project
complete -F _compprojs new_project

