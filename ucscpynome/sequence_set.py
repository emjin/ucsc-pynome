from . import Sequence
from . import Genome
import sys
import subprocess
import requests
import os.path
from os import path
import gzip

class MalformedBedFileError(Exception):
    pass



class SequenceSet():
    """ Represents a set of sequences pulled from one or more bed files.

    The format of a valid bed file is taken from Wikipedia:
    https://en.wikipedia.org/wiki/BED_(file_format)

    Use methods here to:
        - construct a sequence set from one or more bed files
        - put the coordinates of all sequences in the set into a bed file
        - perform liftover on a sequence set from one genome to another

    Attributes: (all are read-only)
        genome (str): name of genome to which sequences belong
        sequences (list of Sequence): list of sequences in set

    Raises:
        TypeError: if constructor is passed a single bed file name rather than a list
        MalformedBedFileError: if bed file cannot be successfully parsed
        OSError: if a file cannot be opened or created
    """
    
    MIN_NUM_COLS = 3
    CHROM_COL = 0
    START_COL = 1
    END_COL = 2

    def __init__(self, bed_file_names, genome):
        if not isinstance(bed_file_names, list):
            raise TypeError("bed_file_names should be of type list")

        self.genome = genome
        self.sequences = list()
        for filename in bed_file_names:
            self.__parse_bed_file(filename)

    def __is_header_line(self, L):
        """ Check if the given line is part of the header of a bed file

        :param L: line of bed file to check
        :return: true if header starts with "browser", "track", or "#" as specified by Wikipedia
        """
        first_word = L[0]
        return first_word == "browser" or first_word == "track" or first_word == "#"

    def __parse_bed_file(self, bed_file_name):
        """ Parse given bed file and place its sequences into set

        Raises:
            OSError: if file cannot be opened or read
            MalformedBedFileError: if file does not have correct format

        :param bed_file_name: file to read sequence data from (chromosome, start, end, label)
        """
        curr_file_sequences = list()
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
                        raise MalformedBedFileError("Number of columns is not the same across all lines in file: " + bed_file_name)
                    if len(L) > self.MIN_NUM_COLS:
                        # there is additional line data
                        additional_cols = L[self.MIN_NUM_COLS:]
                        label = " ".join(additional_cols)
                        seq = Sequence(L[self.START_COL], L[self.END_COL], self.genome,
                                            L[self.CHROM_COL], label)
                        curr_file_sequences.append(seq)
                    else:
                        seq = Sequence(L[self.START_COL], L[self.END_COL],
                                            self.genome, L[self.CHROM_COL])
                        curr_file_sequences.append(seq)
        # successfully parsed bed file
        self.sequences.extend(curr_file_sequences)
    
    def to_bed(self, bed_file_name):
        """Dump the sequence set data into a single bed file.

        WARNING: If bed_file_name already exists, this will overwite that file.

        Raises:
            OSError: if bed_file_name cannot be opened with write permissions

        :param bed_file_name: name of file to which to write sequence set
        """
        f = open(bed_file_name, "w")
        for sequence in self.sequences:
            f.write(sequence.chromosome)
            f.write("\t")
            f.write(sequence.start)
            f.write("\t")
            f.write(sequence.end)
            if sequence.label != None:
                f.write("\t")
                f.write(sequence.label)
            f.write("\n")
        f.close()

    def to_fasta(self, fasta_file_name):
        """Dump actual sequence strings from sequence set into a fasta file.

        WARNING: If fasta_file_name already exists, this will overwite that file.

        The call to sequence.string() may cause a network request if the sequence
        string has not been populated yet.

        Raises:
            OSError: if fasta_file_name cannot be opened with write permissions
            NetworkError: if cannot download sequence string

        :param fasta_file_name: name of fasta file
        """
        f = open(fasta_file_name, "w")
        for seq in self.sequences:
            seq_string = seq.string()
            f.write(">")
            if seq.label != None:
                f.write(seq.label)
            f.write("\n")
            f.write(seq_string)
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
