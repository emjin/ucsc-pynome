import sys
sys.path.append("../..")
from ucscpynome import Genome
import os

if not os.path.exists('mammals'):
    os.makedirs('mammals')

mammals = ["bosTau9", "canFam4", "choHof1", "dasNov3", "dipOrd1", "echTel1"]

for mammal in mammals:
    Genome.download_sequence(Genome(mammal), "mammals/", include_pseudochromosomes=True)