import sys
sys.path.append("../..")
from ucscpynome import Genome
from ucscpynome import SequenceSet

hg19_seqs = SequenceSet(["hg19_ex.bed"], "hg19")
primates = ["panTro6", "ponAbe3", "rheMac10"]

intersecting_seqs = set()

# Get sequences for each primate
for primate in primates:
    print("Starting " + primate)
    primate_gene = SequenceSet.liftover(hg19_seqs, Genome(primate))

    # Go through the sequences and check if any of them exactly match one of the human ones
    for primate_seq in primate_gene.sequences:
        for human_seq in hg19_seqs.sequences:
            if human_seq.string is primate_seq.string:
                intersecting_seqs.add(human_seq)

hg19_seqs.sequences = list(set(hg19_seqs.sequences) - intersecting_seqs)
hg19_seqs.to_fasta("hg19_unique.fasta")