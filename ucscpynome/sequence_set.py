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

    def __init__(self, bed_file_names, genome):
        self.genome = genome
        self.coordinates = list()
        for filename in bed_file_names:
            try:
                self.__parse_bed_file(filename)
            except (OSError, MalformedBedFileError) as e:
                print(repr(e))
                print("Unable to parse bed file " + filename)
            else:
                print("Successfully parsed bed file " + filename)

    def __is_header_line(self, L):
        first_word = L[0]
        return first_word == "browser" or first_word == "track" or first_word == "#"

    def __parse_bed_file(self, bed_file_name):
        curr_file_coordinates = list()
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
                            raise MalformedBedFileError("Not enough columns")
                    elif len(L) != num_columns:
                        raise MalformedBedFileError("Number of columns is not the same across all lines")
                    if len(L) > self.MIN_NUM_COLS:
                        # there is additional line data
                        additional_cols = L[self.MIN_NUM_COLS:]
                        label = " ".join(additional_cols)
                        coord = Sequence(L[self.START_COL], L[self.END_COL], self.genome, 
                                            L[self.CHROM_COL], label)
                        curr_file_coordinates.append(coord)
                    else:
                        coord = Sequence(L[self.START_COL], L[self.END_COL], 
                                            self.genome, L[self.CHROM_COL])
                        curr_file_coordinates.append(coord)
        # successfully parsed bed file
        self.coordinates.extend(curr_file_coordinates)
    
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
            seq = coord.string() # TODO what to do if this fails?
            f.write(">")
            if coord.label != None:
                f.write(coord.label)
            f.write("\n")
            f.write(seq)
            f.write("\n")
        f.close()
    
    # Liftover functionality
    def liftover(self, target_genome, path_to_chain = None):
        """
            Perform liftover to a specified genome.
            Wrapper around liftover method of Genome class.

            This method generates and saves additional files when necessary: 

            bed files (always):
                {self.genome}.bed
                {target_genome}.bed

            log file (always): 
                {src_genome}To{target_genome}_liftover_log.err

            chain files (if not specified):
                {src_genome}To{Target_genome}.over.chain.gz
                {src_genome}To{Target_genome}.over.chain

            unmapped file (always):
                {src_genome}To{target_genome}_unmapped.bed


            This method saves all generated files inside /liftover_files directory, which
            has three subdirectories:

            /bed_files      : bed files created by ucscpynome in the process of liftover,
                              including unmapped.bed files.
            /chain_files    : chain files downloaded (when path_to_chain is not specified).
            /log_files      : logs generated by UCSC's liftOver tool
  
            Params:
                target_genome (Genome): genome to liftover to
                path_to_chain (string): optional parameter to specify the path to a
                custom chain file to use for the liftover

            Returns:
                SequenceSet: a new object representing the lifted genome

            Raises:
                LookupError: If the chain file for the specified target genome doesn't 
                exist.
                LiftoverError: If there is an error during liftover using UCSC's 
                command-line liftover tool.

        """
        BED_FILES_PATH = "liftover_files/bed_files/"
        script_dir = os.path.dirname(__file__)

        src = str(self.genome)
        target = str(target_genome)

        # create and fill in source bed file
        src_file = os.path.join(script_dir, BED_FILES_PATH + src + '.bed')
        self.to_bed(src_file)

        # create target bed file
        target_file = os.path.join(script_dir, BED_FILES_PATH + target + '.bed')

        # call to Genome class static utility method
        if path_to_chain:
            Genome.liftover(self.genome, target_genome, src_file, target_file, 
                            path_to_chain=path_to_chain)
        else:
            Genome.liftover(self.genome, target_genome, src_file, target_file)

        # create a new object of the lifted result
        lifted_sequence = SequenceSet([target_file], target_genome)
        return lifted_sequence
      
            
# tests
def test_hg19_file_creation():
    ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
    ss.to_fasta("hg19_ex.fasta")
    ss.to_bed("hg19_new.bed")

def hg19_to_hg38():
    ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
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
    ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
    lss = ss.liftover(Genome("hg38"), "test_files/bad_hg19_hg38.over.chain")

# hg19_to_hg38()
# print(ss.coordinates[0].genome)
# print(ss.coordinates[0].chromosome)
# print(ss.coordinates[0].start)
# print(ss.coordinates[0].end)
# ss = SequenceSet("hg19_new.bed", "hg19")
# ss.convert_to_bed("hg19_new2.bed")
# tests TODO should test out label functionality for convert_to_bed
# should also test out failure cases
