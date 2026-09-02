# tbtools-cli bash completion
# 安装: source completions/tbtools_completion.bash
# 或: cp completions/tbtools_completion.bash /etc/bash_completion.d/tbtools

_tbtools_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    local _root="$(dirname "$(dirname "$(readlink -f "${COMP_WORDS[0]}")")")"

    if [ $COMP_CWORD -eq 1 ]; then
        opts="version doctor help list tool plot engine rpc methods server heatmap"
        opts="$opts $(bash "$_root/bin/tbplot.sh" help 2>/dev/null | grep -oE '^[a-zA-Z0-9]+' | sort -u | tr '\n' ' ')"
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
        return 0
    fi

    case "${COMP_WORDS[1]}" in
        tool)
            [ $COMP_CWORD -eq 2 ] && COMPREPLY=($(compgen -W "$(tbtools list tools 2>/dev/null | grep -oE '^[a-zA-Z0-9]+' | tr '\n' ' ')" -- "$cur"))
            ;;
        list)
            [ $COMP_CWORD -eq 2 ] && COMPREPLY=($(compgen -W "tools plots rpc all" -- "$cur"))
            ;;
        rpc)
            [ $COMP_CWORD -eq 2 ] && COMPREPLY=($(compgen -W "call describe methods start stop" -- "$cur"))
            ;;
        server)
            [ $COMP_CWORD -eq 2 ] && COMPREPLY=($(compgen -W "start stop" -- "$cur"))
            ;;
    esac

    case "$prev" in
        -o|--out|--outFile|--outPutFile|--outGraph|--outTab|--outTable)
            COMPREPLY=($(compgen -f -- "$cur"))
            ;;
    esac
}
complete -F _tbtools_complete tbtools 2>/dev/null || true
complete -F _tbtools_complete tbplot.sh 2>/dev/null || true
