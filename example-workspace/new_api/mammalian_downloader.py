import sys
sys.path.append("../..")
from ucscpynome import Genome

mammals = ["bosTau9", "canFam4", "choHof1", "dasNov3", "dipOrd1", "echTel1"]

for mammal in mammals:
    Genome.download_sequence(Genome(mammal), "mammals/")