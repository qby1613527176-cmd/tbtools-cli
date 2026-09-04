#!/usr/bin/env bash
# Bash completion for tbtools-cli
# Install: cp scripts/tbtools-completion.bash ~/.local/share/bash-completion/completions/tbtools
# Or: source scripts/tbtools-completion.bash in ~/.bashrc

_tbtools_complete() {
    local cur prev words cword
    _init_completion || return

    local groups="seq expr tree syn sets chipseq asm gxf mirna table blast fastq hmm gwas engine"
    local top_cmds="version doctor examples list presets tool help rpc"

    if [ $cword -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$groups $top_cmds" -- "$cur") )
        return
    fi

    local cmd="${words[1]}"
    if [ $cword -ge 2 ]; then
        case "$cmd" in
            tool)
                # List tool subcommands from auto_commands (non-plot only)
                local tools=$(python3 -c "
import sys; sys.path.insert(0, '$PWD')
import tbtools_cli.auto_commands as ac
plot = {'seq','expr','tree','syn','sets','chipseq'}
try:
    from tbtools_cli.cli import CATEGORY_MAP
except Exception:
    CATEGORY_MAP = {}
for n in sorted(dir(ac)):
    if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
        cmd = n[1:-5]
        if CATEGORY_MAP.get(cmd, 'engine') not in plot:
            print(cmd, end=' ')
" 2>/dev/null)
                COMPREPLY=( $(compgen -W "$tools stat-fasta cds2protein fasta-extract" -- "$cur") )
                ;;
            help)
                # help 补全：所有分组命令
                local all_cmds=$(python3 -c "
import sys; sys.path.insert(0, '$PWD')
from tbtools_cli.cli import _groups
for gname, g in _groups.items():
    for c in g.commands:
        print(c, end=' ')
" 2>/dev/null)
                COMPREPLY=( $(compgen -W "$all_cmds version doctor list presets tool help rpc" -- "$cur") )
                ;;
            list)
                COMPREPLY=( $(compgen -W "plots tools rpc" -- "$cur") )
                ;;
            rpc)
                COMPREPLY=( $(compgen -W "start methods call" -- "$cur") )
                ;;
            presets)
                COMPREPLY=( $(compgen -W "nature cell presentation poster" -- "$cur") )
                ;;
            seq|expr|tree|syn|sets|chipseq|asm|gxf|mirna|table|blast|fastq|hmm|gwas|engine)
                # 分组子命令补全
                local subs=$(python3 -c "
import sys; sys.path.insert(0, '$PWD')
from tbtools_cli.cli import _groups
g = _groups.get('$cmd')
if g:
    print(' '.join(g.commands.keys()))
" 2>/dev/null)
                COMPREPLY=( $(compgen -W "$subs" -- "$cur") )
                ;;
        esac
    fi
}

complete -F _tbtools_complete tbtools
