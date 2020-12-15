from sequence import Sequence
from genome import Genome
import sys
import subprocess
import requests
import os.path
from os import path
import gzip

class MalformedBedFileError(Exception):
    pass

class SequenceSet():
    """TODO

    """
    
    MIN_NUM_COLS = 3
    CHROM_COL = 0
    START_COL = 1
    END_COL = 2
    NAME_COL = 3

    def __init__(self, bed_file_name, genome):
        self.genome = genome
        self.__parse_bed_file(bed_file_name)

    def __is_header_line(self, L):
        first_word = L[0]
        return first_word == "browser" or first_word == "track" or first_word == "#"

    def __parse_bed_file(self, bed_file_name):
        self.coordinates = list()
        with open(bed_file_name) as f:
            num_columns = -1
            for line in f:
                L = line.strip().split()
                if len(L) == 0:
                    break
                if not self.__is_header_line(L):
                    if num_columns == -1:
                        num_columns = len(L)
                        if num_columns < self.MIN_NUM_COLS:
                            return MalformedBedFileError("Not enough columns")
                    elif len(L) != num_columns:
                        return MalformedBedFileError("Number of columns is not the same across all lines")
                    if len(L) > self.MIN_NUM_COLS:
                        # there is additional line data
                        coord = Sequence(L[self.START_COL], L[self.END_COL], self.genome, 
                                            L[self.CHROM_COL], L[self.NAME_COL])
                        self.coordinates.append(coord)
                    else:
                        coord = Sequence(L[self.START_COL], L[self.END_COL], 
                                            self.genome, L[self.CHROM_COL])
                        self.coordinates.append(coord)
    
    # will overwrite existing file if bed_file_name already exists
    def to_bed(self, bed_file_name):
        """TODO

        """
        f = open(bed_file_name, "w")
        for coord in self.coordinates:
            f.write(coord.chromosome)
            f.write("\t")
            f.write(coord.start)
            f.write("\t")
            f.write(coord.end)
            if coord.label != None:
                f.write("\t")
                f.write(coord.label)
            f.write("\n")
        f.close()

    def to_fasta(self, fasta_file_name):
        """TODO

        """
        f = open(fasta_file_name, "w")
        for coord in self.coordinates:
            seq = coord.get_sequence() # TODO what to do if this fails?
            f.write(">")
            if coord.label != None:
                f.write(coord.label)
            f.write("\n")
            f.write(seq)
            f.write("\n")
        f.close()
    
    # Liftover functionality
    def liftover(self, target_genome, chain = None):
        """TODO

        """
        src = str(self.genome)
        target = str(target_genome)

        src_file = "temp/liftover_temp_file_" + src + '.bed'
        self.to_bed(src_file)

        target_file = "temp/liftover_temp_file_" + target + '.bed'

        # call to Genome class' static utility method
        if chain:
            Genome.liftover(self.genome, target_genome, src_file, target_file, path_to_chain=chain)
        else:
            Genome.liftover(self.genome, target_genome, src_file, target_file)

        lifted_sequence = SequenceSet(target_file, target_genome)
        return lifted_sequence
      
            
# tests
def test_hg19_file_creation():
    ss = SequenceSet("test_files/hg19_ex.bed", "hg19")
    ss.create_fasta("hg19_ex.fasta")
    ss.to_bed("hg19_new.bed")

def hg19_to_hg38():
    ss = SequenceSet("test_files/hg19_ex.bed", "hg19")
    lss = ss.liftover(Genome("hg38"))

def nonexistent_file():
    ss = SequenceSet("test_files/hg17_ex.bed", "hg19")
    lss = ss.liftover(Genome("hg38"))

def nonexistent_src():
    ss = SequenceSet("test_files/hg19_ex.bed", "jf89")
    lss = ss.liftover(Genome("hg38"))

def bad_src_file():
    ss = SequenceSet("test_files/hg19_bad.bed", "hg19")
    lss = ss.liftover(Genome("hg38"))

def wrong_col_count():
    ss = SequenceSet("test_files/hg19_bad2.bed", "hg19")
    lss = ss.liftover(Genome("hg38"))

def bad_chain_file():
    # should raise LiftoverError
    ss = SequenceSet("test_files/hg19_ex.bed", "hg19")
    lss = ss.liftover(Genome("hg38"), "test_files/bad_hg19_hg38.over.chain")

hg19_to_hg38()

# print(ss.coordinates[0].genome)
# print(ss.coordinates[0].chromosome)
# print(ss.coordinates[0].start)
# print(ss.coordinates[0].end)
# ss = SequenceSet("hg19_new.bed", "hg19")
# ss.convert_to_bed("hg19_new2.bed")
# tests TODO should test out label functionality for convert_to_bed
# should also test out failure cases
