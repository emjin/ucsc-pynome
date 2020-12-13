
import requests

class InvalidGenomeError(ValueError):
    pass

class InvalidChromosomeError(ValueError):
    pass

class InvalidOrganismError(ValueError):
    pass

class Genome():
    __genome_dict = {}
    __organism_dict = {}
    
    # constructs one instance of the class for each unique genome
    # populates all possible genomes in the genome dictionary the first
    # time it's called, returns corresponding instance when requested
    def __new__(cls, genome):
        if len(Genome.__genome_dict) > 0:
            if genome in Genome.__genome_dict:
                return Genome.__genome_dict[genome]
            else:
                raise InvalidGenomeError(genome + " is not a valid genome")
        else: # call web api and populate the genome dict
            url = "http://api.genome.ucsc.edu/list/ucscGenomes"
            response = requests.get(url)
            info = response.json()
            for g,data in info['ucscGenomes'].items():
                instance = super().__new__(cls)
                instance.__chromosomes = []
                instance.genome = g 
                Genome.__genome_dict[g] = instance
                org = data["organism"].lower()
                if org in Genome.__organism_dict:
                    Genome.__organism_dict[org].append(g)
                else:
                    Genome.__organism_dict[org] = [g]
            if genome in Genome.__genome_dict:
                return Genome.__genome_dict[genome]
            else:
                raise InvalidGenomeError(genome + " is not a valid genome")

    # helper to get the sequence for a specific chromosome in the genome
    def __get_chrom_sequence(self, chromosome):
        url = "http://api.genome.ucsc.edu/getData/sequence?genome="
        url += self.genome + ";chrom="
        url += chromosome
        response = requests.get(url)
        info = response.json()
        
        if response.status_code in [200, 201, 202, 204]:
            return info['dna']

        elif response.status_code == 400:
            raise InvalidChromosomeError("could not find chromosome " + chromosome + " in genome")
        
    # returns entire sequence for a genome for every chromosome if it is not specified
    # else, returns entire sequence for that chromosome
    def get_sequence(self, chromosome=None):
        if chromosome == None:
            chromosomes = self.list_chromosomes()
            # currently we're just storing everything to a string, don't know if we want to separate by chromosome
            # or maybe output to a file
            seq = "" 
            for chrom in chromosomes: 
                seq += self.__get_chrom_sequence(chrom)
            return seq
        else:
            return self.__get_chrom_sequence(chromosome)
    
    # lists all chromosomes for a genome
    # lazily populates chromosomes for the genome, only fetches once
    def list_chromosomes(self):
        if len(self.__chromosomes) == 0:
            url = "http://api.genome.ucsc.edu/list/chromosomes?genome="
            url += self.genome
            response = requests.get(url)
            info = response.json()
            chromosome_list = []
            for chromosome in info["chromosomes"]:
                chromosome_list.append(chromosome)
            self.__chromosomes = chromosome_list
        return self.__chromosomes
       
    #static utility method for getting genomes 
    #returns genomes for a specified organism
    #else returns list of all genomes available 
    def list_genomes(organism=None):
        if organism == None:
            if len(Genome.__genome_dict) == 0:
                url = "http://api.genome.ucsc.edu/list/ucscGenomes"
                response = requests.get(url)
                info = response.json()
                for g,data in info['ucscGenomes'].items():
                    genome_obj = Genome(g)
                    Genome.__genome_dict[g] = genome_obj
                    org = data["organism"].lower()
                    if org in Genome.__organism_dict:
                        Genome.__organism_dict[org].append(g)
                    else:
                        Genome.__organism_dict[org] = [g]
            return Genome.__genome_dict.keys()
        else:
            if organism.lower() in Genome.__organism_dict:
                return Genome.__organism_dict[organism.lower()]
            else:
                raise InvalidOrganismError(organism + " is not a valid organism")

g1 = Genome("hg38")
print(g1.get_sequence("chr1"))
# g1.list_chromosomes()
# g1.list_chromosomes()
# g2 = Genome("hg38")
# g3 = Genome("hg19")
# print(g1)
# print(g2)
# print(g3)
# print(Genome.list_genomes("kangaroo rat"))
