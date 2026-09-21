import io
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# blast xml（供 pileup）
os.system('C:/Users/16135/.workbuddy/binaries/python/envs/default/Scripts/python.exe -m tbtools_cli.cli blast twoSeqBlast --query out/pin10.fa --subject data/monarda_chloro_pep.fa --outBlastResult out/t2b5.xml --outFmt 5 --thread 4')
# pin10_rank.rnk（真实 bitscore）
sc = {}
for l in io.open("out/blast_atpin_si.tab"):
    f = l.rstrip("\n").split("\t"); q = f[0].split()[0]
    b = float(f[11])
    if q not in sc or b > sc[q]: sc[q] = b
pin10 = [l.split()[0][1:] for l in io.open("out/pin10.fa") if l.startswith(">")]
io.open("out/pin10_rank.rnk", "w", newline="\n").write(
    "".join(f"{g}\t{sc.get(g, 0):.1f}\n" for g in pin10))
W = lambda p, s: io.open(p, "w", newline="\n").write(s)
W("out/admix.lst", "out/fake_Q.txt\n")
W("out/fake_Q.txt", "0.9\t0.1\n0.8\t0.2\n0.5\t0.5\n0.6\t0.4\n")
W("out/pattern_map.tsv", "Root\tRootSyn\nLeaf\tLeafSyn\n")
W("out/fake.sam", "@HD\tVN:1.6\n")
paf = "q1\t100\t0\t100\t+\tmonarda_chloro\t151812\t1000\t1100\t100\t100\t60\tcg:Z:100M\n"
W("out/fake.paf", paf); W("out/fake1.paf", paf)
W("out/fake2.paf", "q1\t100\t0\t100\t+\tmonarda_chloro\t151812\t1000\t1100\t100\t100\t55\tcg:Z:100M\n")
W("out/fake.gfa", "H\tVN:Z:1.0\nS\t1\tACGT\n")
W("out/upset_sets.txt", "AtPIN\tout/at_ids.txt\nSiPIN\tout/si_ids.txt\n")
W("out/degramdom_in.tsv", "At_PIN1\tAt_PIN2\t0.1\nAt_PIN2\tAt_PIN4\t0.2\n")
W("out/seq1.txt", "MKTAYIAKQRQISFVKSHFSRQ\n")
W("out/seq2.txt", "MKTAYIAKQRQISFVKSHFSEK\n")
W("out/gel_cfg.txt", "[LaneLabels]\nM,S1,S2\n[MarkerRange]\n10000,250\n[FragmentRangeArr]\n10000,3000,1000,250;5000,2500,750,250;5000,2500,750,250;5000,2500,750,250\n")
W("out/circos_link.txt", "monarda_chloro\t1000\t5000\tmonarda_chloro\t50000\t54000\n")
W("out/fake.pfam.hmm", "HMMER3/f [i1]\n")
W("out/targetso.tsv", "miR156\tGTGCTTCTCTCTCTTCTGTCA\n")
W("out/cdd_hitdata.txt", "At_PIN1_Q9C6B8\tcd00123\t10\t200\t1e-40\n")
W("out/fake_ctl.txt", "[data]\n")
W("out/supercircos_cfg.txt", "[chrLen]\nmonarda_chloro\t151812\n")
W("out/treetab_cfg.txt", "[TYPE]:Tree\n[NEWICK]:(A:1,B:1);\n")
os.makedirs("out/mcscanx_wd", exist_ok=True)
print("extra inputs OK; xml exists:", os.path.isfile("out/t2b5.xml"))

