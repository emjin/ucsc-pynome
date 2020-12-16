import unittest
import sys
sys.path.append("..")
from ucscpynome import Requests
from ucscpynome import Sequence



class TestSequence(unittest.TestCase):
    
    def setUp(self):
        self.newSeq = Sequence(1234, 5678, "hg38", "chrM")

    #test output of printing sequence info
    def test_print_sequence(self):
       self.assertTrue((str(self.newSeq)) == "{'start': 1234, 'end': 5678, 'genome': 'hg38', 'chromosome': 'chrM'}")

    #ensure sequence string is same object and saved due to lazy evaluation
    #ensures the length is the equal to the difference of the coordinates
    def test_sequence_string(self):
        self.assertTrue(self.newSeq.string() is self.newSeq.string())
        self.assertEqual(len(str(self.newSeq.string())),(5678-1234))


    


if __name__ == '__main__':
    unittest.main()