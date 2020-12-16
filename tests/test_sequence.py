import unittest
from unittest import mock
import sys
sys.path.append("..")
from ucscpynome import Requests
from ucscpynome import Sequence

TEST_GENOME = "hg38"
TEST_CHROM = "chrM"
TEST_CHROM_START = 1234
TEST_CHROM_END = 1250

SEQUENCE_KEY = "dna"

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if str(TEST_CHROM_START) in args[0] and str(TEST_CHROM_END) in args[0]:
        return MockResponse({SEQUENCE_KEY: "TCACCACCTCTTGCTC"}, 200)

    return MockResponse(None, 404)



class TestSequence(unittest.TestCase):
    
    def setUp(self):
        self.newSeq = Sequence(TEST_CHROM_START, TEST_CHROM_END, TEST_GENOME, TEST_CHROM)

    # test output of printing sequence info
    def test_print_sequence(self):
        expected_seq = f"{{'start': {TEST_CHROM_START}, 'end': {TEST_CHROM_END}, " \
                       f"'genome': '{TEST_GENOME}', 'chromosome': '{TEST_CHROM}'}}"
        self.assertTrue((str(self.newSeq)) == expected_seq)

    # ensure sequence string is same object and saved due to lazy evaluation
    # ensures the length is the equal to the difference of the coordinates
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_sequence_string(self, mock_get):
        self.assertTrue(self.newSeq.string() is self.newSeq.string())
        self.assertEqual(len(str(self.newSeq.string())),(TEST_CHROM_END-TEST_CHROM_START))

    # ensure users can't change immutable sequence attributes
    def test_sequence_immutable(self):
        def immutable_help():
            self.newSeq.start = 15
        self.assertRaises(AttributeError, immutable_help)
        def immutable_help2():
            self.newSeq.end = 15
        self.assertRaises(AttributeError, immutable_help2)
        def immutable_help3():
            self.newSeq.genome = "trash"
        self.assertRaises(AttributeError, immutable_help3)
        def immutable_help4():
            self.newSeq.chromosome = "junk"
        self.assertRaises(AttributeError, immutable_help4)


    


if __name__ == '__main__':
    unittest.main()