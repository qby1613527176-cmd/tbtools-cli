# Workflows

Plan-able end-to-end pipelines. Machine-readable definitions in [`ai/workflows.json`](../ai/workflows.json) (each step = tool id + role; inputs/outputs chained).

## Gene Family Analysis (GRAS-verified)

```text
FASTA → muscle (MSA) → trimal (trim) → iqtree (phylogeny) → motif (MEME) → genestructure (gene structure SVG)
```

```bash
tbtools seq muscle family.fa aln.fa
tbtools seq trimal aln.fa aln.trim.fa
tbtools tree iqtree aln.trim.fa
tbtools seq motif family.fa
tbtools seq structure genes.gff ids.txt out.svg
```

## RNA-seq (DEG)

```text
counts → tpmCalc (normalize) → pca (QC) → heatmap (viz) → volcano (DEG)
```

```bash
tbtools tool tpmCalc counts.tsv len.tsv out.tsv
tbtools expr pca out.tsv pca.svg
tbtools expr heatmap out.tsv heat.svg
tbtools expr volcano deg.txt volcano.svg
```

## Comparative Genomics (Synteny)

```text
GFF + BLAST → mcscanx (collinearity) → dualsyn / dotplot (viz)
```

```bash
tbtools syn mcscanx gff.txt blast.tab6 col.txt
tbtools syn dualsyn simple.gff col.txt dual.svg --chr1 1 --chr2 2
tbtools syn dotplot --inGff gff.txt --genePair col.txt --chrLayout layout.txt
```

## Phylogeny

```text
FASTA → msa (align) → trimal (trim) → one-step (IQ-TREE) → tree draw
```

```bash
tbtools seq msa aln.fa aln.svg
tbtools seq trimal aln.fa aln.trim.fa
tbtools tree onesteptree aln.trim.fa out
tbtools tree draw out.nwk tree.svg
```

## Agent-driven

```bash
tbtools search "differential expression" --json          # 1 discover
tbtools tool-describe volcano --json                     # 2 understand
tbtools tool-validate volcano deg.txt --json             # 3 preflight
tbtools tool-run expr volcano deg.txt out.svg --json     # 4 execute (pure JSON)
tbtools tool-provenance out.svg                          # 5 audit
```

Example data for all workflows: [`examples/data/`](https://github.com/qby1613527176-cmd/tbtools-cli/tree/main/examples/data).
