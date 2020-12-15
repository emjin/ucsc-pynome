import unittest
import os
import sys
sys.path.append("..")
from ucscpynome import Genome

class TestGenome(unittest.TestCase):
    def setUp(self):
        self.hg_genome = Genome("hg38")

    def test_list_genome(self):
        # Returns list of all genomes available
        genome_list = Genome.list_genomes()
        self.assertTrue(len(genome_list) > 0)
        self.assertEqual(list(genome_list).count("hg38"), 1)
        self.assertEqual(list(genome_list).count("hg19"), 1)
        self.assertEqual(list(genome_list).count("dipOrd1"), 1)

        # Lists all genomes of a cow, case-insensitive
        self.assertEqual(Genome.list_genomes("cow"), ['bosTau2', 'bosTau3', 'bosTau4', 'bosTau6', 'bosTau7', 'bosTau8', 'bosTau9'])
        self.assertEqual(Genome.list_genomes("Cow"), ['bosTau2', 'bosTau3', 'bosTau4', 'bosTau6', 'bosTau7', 'bosTau8', 'bosTau9'])
        self.assertEqual(Genome.list_genomes("COW"), ['bosTau2', 'bosTau3', 'bosTau4', 'bosTau6', 'bosTau7', 'bosTau8', 'bosTau9'])
        self.assertEqual(Genome.list_genomes("CoW"), ['bosTau2', 'bosTau3', 'bosTau4', 'bosTau6', 'bosTau7', 'bosTau8', 'bosTau9'])
        self.assertTrue('dipOrd1' in Genome.list_genomes("kangaroo rat")) #ensure it exists
        self.assertEqual(Genome.list_genomes("kangaroo rat").count("dipOrd1"), 1) #ensure no duplicates in list

    def test_init(self):
        # Create a genome from a string, ensures they are the same object
        hg_genome2 = Genome("hg38")
        self.assertTrue(self.hg_genome is hg_genome2)

    def test_list_chromosomes(self):
        # Find a genome of a animal and list all chromosomes of it
        kgrat = Genome.list_genomes("kangaroo rat")
        kg_genome = Genome(kgrat[0])

    def test_download_sequence(self):
        # Downloads one chromosome for a genome and deletes it
        # Ensures no errors
        self.hg_genome.download_sequence("temp", "chrM")
        os.remove("temp_hg38_chrM")

        # Downloads entire genome for C. elegans and deletes it
        ce_genome = Genome("ce2")
        ce_genome.download_sequence("temp")
        for chrom in ce_genome.list_chromosomes():
            os.remove("temp_ce2_" + chrom)        

    def test_list_chromosomes(self):
        #lists all chromosomes for a genome -- hg38
        chromosome_list = self.hg_genome.list_chromosomes()
        self.assertTrue(len(chromosome_list) > 0)
        self.assertEqual(list(chromosome_list).count("chr1"), 1)
        self.assertEqual(list(chromosome_list).count("chrM"), 1)
