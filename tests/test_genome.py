import unittest
from unittest import mock
import os
import sys
sys.path.append("..")
from ucscpynome import Genome

TEST_GENOME = "hg38"
TEST_CHROM_M = "chrM"
TEST_CHROM_1 = "chr1"

TEST_ORG = "human"

CHROMOSOMES_KEY = "chromosomes"
GENOMES_KEY = "ucscGenomes"
ORGANISM_KEY = "organism"
TEST_CHROMOSOMES_JSON = {TEST_CHROM_1: 1234, TEST_CHROM_M: 5678}
TEST_GENOMES_JSON = {TEST_GENOME: {ORGANISM_KEY: TEST_ORG}}

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    # list chromosomes
    print(args[0])
    if f"list/chromosomes?genome={TEST_GENOME}" in args[0]:
        return MockResponse({CHROMOSOMES_KEY: TEST_CHROMOSOMES_JSON}, 200)
    elif "list/ucscGenomes" in args[0]:
        return MockResponse({GENOMES_KEY: TEST_GENOMES_JSON}, 200)

    return MockResponse(None, 404)


class TestGenome(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def setUp(self, mock_get):
        self.hg_genome = Genome(TEST_GENOME)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_list_genome(self, mock_get):
        # Returns list of all genomes available
        genome_list = Genome.list_genomes()
        self.assertTrue(len(genome_list) > 0)
        self.assertEqual(list(genome_list).count(TEST_GENOME), 1)

        # Lists all genomes, case-insensitive
        self.assertEqual(Genome.list_genomes(TEST_ORG.lower()), [TEST_GENOME])
        self.assertEqual(Genome.list_genomes(TEST_ORG.upper()), [TEST_GENOME])
        self.assertTrue(TEST_GENOME in Genome.list_genomes(TEST_ORG)) #ensure it exists
        self.assertEqual(Genome.list_genomes(TEST_ORG).count(TEST_GENOME), 1) #ensure no duplicates in list

    def test_init(self):
        # Create a genome from a string, ensures they are the same object
        hg_genome2 = Genome(TEST_GENOME)
        self.assertTrue(self.hg_genome is hg_genome2)

    def test_list_chromosomes_animal(self):
        # Find a genome of a animal and list all chromosomes of it
        kgrat = Genome.list_genomes("kangaroo rat")
        kg_genome = Genome(kgrat[0])

    def test_download_sequence(self):
        # Downloads one chromosome for a genome and deletes it
        # Ensures no errors
        self.hg_genome.download_sequence("temp", TEST_CHROM_M)
        os.remove(f"temp_{TEST_GENOME}_{TEST_CHROM_M}")

        # Downloads entire genome for C. elegans and deletes it
        ce_genome = Genome("ce2")
        ce_genome.download_sequence("temp")
        for chrom in ce_genome.list_chromosomes():
            os.remove("temp_ce2_" + chrom)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_list_chromosomes_all(self, mock_get):
        #lists all chromosomes for a genome -- hg38
        chromosome_list = self.hg_genome.list_chromosomes()
        print(chromosome_list)
        self.assertTrue(len(chromosome_list) > 0)
        self.assertEqual(list(chromosome_list).count(TEST_CHROM_1), 1)
        self.assertEqual(list(chromosome_list).count(TEST_CHROM_M), 1)
