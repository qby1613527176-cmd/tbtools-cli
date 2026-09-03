#!/usr/bin/env bash
# Bash completion for tbtools-cli
# Install: cp scripts/tbtools-completion.bash ~/.local/share/bash-completion/completions/tbtools
# Or: source scripts/tbtools-completion.bash in ~/.bashrc

_tbtools_complete() {
    local cur prev words cword
    _init_completion || return

    local groups="seq expr tree syn sets chipseq asm gxf mirna table blast fastq hmm gwas engine"
    local top_cmds="version doctor examples list presets tool"

    if [ $cword -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$groups $top_cmds" -- "$cur") )
        return
    fi

    local cmd="${words[1]}"
    if [ $cword -ge 2 ]; then
        case "$cmd" in
            tool)
                # List tool subcommands from auto_commands
                local tools=$(python3 -c "
import sys; sys.path.insert(0, '$PWD')
import tbtools_cli.auto_commands as ac
for n in sorted(dir(ac)):
    if n.startswith('_') and n.endswith('_impl') and not n.startswith('__'):
        print(n[1:-5], end=' ')
" 2>/dev/null)
                COMPREPLY=( $(compgen -W "$tools stat-fasta cds2protein fasta-extract" -- "$cur") )
                return
                ;;
            expr)
                COMPREPLY=( $(compgen -W "volcano heatmap pca hclust dehist qpcr qpcrExp groupedbar barplot layoutheatmap cubeheatmap violin colorscheme distance mountain tauIndex exprCorr groupCol efpHeat multiEfp" -- "$cur") )
                return
                ;;
            seq)
                COMPREPLY=( $(compgen -W "logo msa structure motif seqlentrack amazingmeta cddmotif pfammotif memerun mastrun mastExtract mast2tab pep2codon simplehmmscan gel gfa gfa2fa plotrna rnaplot" -- "$cur") )
                return
                ;;
            tree)
                COMPREPLY=( $(compgen -W "draw unrooted rooting one-step phylotree degramdom findpath nwAlign" -- "$cur") )
                return
                ;;
            syn)
                COMPREPLY=( $(compgen -W "circos supercircos circlegene dotplot microsyn msy multisyn dualsyn pafviz pafcomp pafref mcscanx collinearRegion findblockdual findblockmultiple visualizeblock conflictpaf partitionconflict microgenome" -- "$cur") )
                return
                ;;
            sets)
                COMPREPLY=( $(compgen -W "venn2 venn3 venn4 venn5 venn6 upset" -- "$cur") )
                return
                ;;
        esac
    fi

    # File completion for remaining args
    COMPREPLY=( $(compgen -f -- "$cur") )
}

complete -F _tbtools_complete tbtools
