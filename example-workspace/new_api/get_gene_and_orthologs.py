import sys
sys.path.append("../..")
from ucscpynome import Genome
from ucscpynome import SequenceSet

hg38_gene = SequenceSet(["gene.bed"], "hg38")
primates = ["panTro6", "ponAbe3", "rheMac10"]

for primate in primates:
    print("Starting " + primate)
    primate_gene = SequenceSet.liftover(hg38_gene, Genome(primate))
    primate_gene.to_bed("genes/" + primate + "_gene.bed")
    primate_gene.to_fasta("genes/" + primate + "_gene.fasta")

hg38_gene.to_fasta("gene.fasta")