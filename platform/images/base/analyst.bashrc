# CyberLab analyst shell
[ -f /etc/bash_completion ] && . /etc/bash_completion
export HISTFILE=/work/.bash_history_lab   # history is kept with your work (useful for your case notes)
export HISTTIMEFORMAT='%F %T UTC  '
export HISTSIZE=5000
shopt -s histappend
PROMPT_COMMAND='history -a'
PS1='\[\e[1;36m\]analyst@${CYBERLAB_LAB:-cyberlab}\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
alias ll='ls -la --color=auto'
alias ls='ls --color=auto'
echo "CyberLab ${CYBERLAB_LAB:-workstation} — evidence: /evidence (read-only)  ·  your work: /work  ·  type 'exit' to leave"
# The root filesystem is read-only: keep tools from trying to write history files to $HOME.
export LESSHISTFILE=-
export VIMINIT='set viminfo= nocompatible backspace=indent,eol,start'
