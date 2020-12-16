import unittest
import os
import sys
sys.path.append("..")
from ucscpynome import SequenceSet, Sequence, Genome
from ucscpynome import MalformedBedFileError, LiftoverError

class TestSequence(unittest.TestCase):
    
    def setUp(self):
        # self.script_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_bed = "../tests/test_files/hg19_ex.bed"
        self.hg19_ss = SequenceSet([path_to_bed], "hg19")

    def content_is_equal(self, file1, file2):
        with open(file1, "r") as file1:
            with open(file2, "r") as file2:
                difference = set(file1).difference(file2)
        
        return (len(difference) == 0)

    def test_hg19_file_creation(self):
        fasta_output = "../tests/test_files/hg19.fasta"
        bed_output = "../tests/test_files/hg19.bed"

        # create fasta and bed files
        self.hg19_ss.to_fasta(fasta_output)
        self.hg19_ss.to_bed(bed_output)

        # compare file content
        self.assertTrue(self.content_is_equal("test_files/hg19.fasta", "test_files/expected_outputs/hg19.fasta"))
        self.assertTrue(self.content_is_equal("test_files/hg19.bed", "test_files/expected_outputs/hg19.bed"))

    def test_hg19_to_hg38(self):
        lss = self.hg19_ss.liftover(Genome("hg38"))

        lss_output = "../ucscpynome/liftover_files/bed_files/hg38.bed"
        unmapped_output = "../ucscpynome/liftover_files/bed_files/hg19Tohg38_unmapped.bed"
        chain_output = "../ucscpynome/liftover_files/chain_files/hg19Tohg38.over.chain"

        # compare file content
        self.assertTrue(self.content_is_equal(lss_output, "test_files/expected_outputs/hg38.bed"))
        self.assertTrue(os.stat(unmapped_output).st_size == 0)
        self.assertTrue(self.content_is_equal(chain_output, "test_files/expected_outputs/hg19Tohg38.over.chain"))

    def test_nonexistent_file(self):
        def no_bed_file():
            ss = SequenceSet(["test_files/hg17_ex.bed"], "hg19")
        self.assertRaises(FileNotFoundError, no_bed_file)
        

    def test_nonexistent_src(self):
        def bad_liftover_target():
            ss = SequenceSet(["test_files/hg19_ex.bed"], "badtarget")
            lss = ss.liftover(Genome("hg38"))
        self.assertRaises(LookupError, bad_liftover_target)

    def test_bad_src_file(self):
        def bad_bed_file():
            ss = SequenceSet(["test_files/hg19_bad.bed"], "hg19")
        self.assertRaises(MalformedBedFileError, bad_bed_file)

    def test_wrong_col_count(self):
        def bad_bed_file2():
            ss = SequenceSet(["test_files/hg19_bad2.bed"], "hg19")
        self.assertRaises(MalformedBedFileError, bad_bed_file2)

    def test_bad_chain_file(self):
        # should raise LiftoverError
        def bad_chain_file():
            ss = SequenceSet(["test_files/hg19_ex.bed"], "hg19")
            lss = ss.liftover(Genome("hg38"), "test_files/bad_hg19_hg38.over.chain")
        self.assertRaises(LiftoverError, bad_chain_file)


if __name__ == '__main__':
    unittest.main()