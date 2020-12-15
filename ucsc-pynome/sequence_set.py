from sequence import Sequence
import sys
import subprocess
import requests
import os.path
from os import path
import gzip

class MalformedBedFileError(Exception):
    pass

class SequenceSet():
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
    
    def liftover(self, target_genome):
        src = self.genome
        target = target_genome

        infile_name = "temp/liftover_temp_file_" + src + '.bed'
        self.to_bed(infile_name)

        outfile_name = "temp/liftover_temp_file_" + target + '.bed'
        unmapped_file = "temp/unmapped.bed"

        chain_name = src + 'To' + target.capitalize() + '.over.chain'
        url = 'https://hgdownload.cse.ucsc.edu/goldenpath/' + src + '/liftOver/' + chain_name + '.gz'
        path_to_chain = 'liftover_files/' + chain_name
        path_to_gz = path_to_chain + '.gz'

        if not path.exists(path_to_chain) and not path.exists(path_to_gz):
            r = requests.get(url, allow_redirects=True)
            if r.status_code != 200:
                raise LookupError("Chain file " + chain_name + " does not exist. There may not be a valid mapping between these genomes")

            gzip.open(path_to_gz, 'wb').write(r.content)
            # TODO: figure out how to close!
        if not path.exists(path_to_chain):
            content = gzip.open(path_to_gz, 'rb').read()
            f = open(path_to_chain, 'wb')
            chain_contents = gzip.decompress(content)
            f.write(chain_contents)
            f.close()

        liftover_call = './liftOver ' + infile_name + ' ' + path_to_chain + ' ' + outfile_name + ' ' + unmapped_file
        redirect = ' 2> log.err'
        os.system(liftover_call + redirect)

        lifted_sequence = SequenceSet([outfile_name], target_genome)
        return lifted_sequence
            
# tests
def test_hg19_file_creation():
    ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
    ss.to_fasta("hg19_ex.fasta")
    ss.to_bed("hg19_new.bed")

def hg19_to_hg38():
    ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
    lss = ss.liftover("hg38")

def nonexistent_file():
    ss = SequenceSet(["test_files/hg17_ex.bed"], "hg19")
    lss = ss.liftover("hg38")

def nonexistent_src():
    ss = SequenceSet(["test_files/hg19_ex.bed"], "jf89")
    lss = ss.liftover("hg38")

def bad_src_file():
    ss = SequenceSet(["test_files/hg19_bad.bed"], "hg19")
    lss = ss.liftover("hg38")

def wrong_col_count():
    ss = SequenceSet(["test_files/hg19_bad2.bed"], "hg19")
    lss = ss.liftover("hg38")

#test_hg19_file_creation()
#hg19_to_hg38()
#wrong_col_count()

# print(ss.coordinates[0].genome)
# print(ss.coordinates[0].chromosome)
# print(ss.coordinates[0].start)
# print(ss.coordinates[0].end)
# ss = SequenceSet("hg19_new.bed", "hg19")
# ss.convert_to_bed("hg19_new2.bed")
# tests TODO should test out label functionality for convert_to_bed
# should also test out failure cases
