import requests

class InvalidGenomeError(ValueError):
    """ InvalidGenomeError is raised when the user inputs an invalid genome """
    pass

class InvalidChromosomeError(ValueError):
    """ InvalidChromosomeError is raised when the user inputs an invalid chromosome """
    pass

class InvalidOrganismError(ValueError):
    """ InvalidOrganismError is raised when the user inputs an invalid organism """
    pass

class Genome():
    """ 
        An instance of Genome represents a genome. Each unique genome only has one
        genome object associated with it. Genomes are equivalent if they represent the
        same genome. A genome object allows users to easily access different functionalities
        related to the genome. The Genome class also contains utility methods common across
        all genomes.

        Raises:
        InvalidGenomeError
        InvalidChromosomeError
        InvalidOrganismError
    """
    __genome_dict = {}
    __organism_dict = {}
    
    def __new__(cls, genome):
        """
            Constructs one instance of the class for each unique genome.

            Params:
            genome (string): the genome to create

            Raises:
            InvalidGenomeError if the input genome is not a valid genome
        """
        # Populates all possible genomes in the genome dictionary the first time
        # the method is called, returns corresponding instance when requested.
        if len(Genome.__genome_dict) > 0:
            if genome in Genome.__genome_dict:
                return Genome.__genome_dict[genome]
            else:
                raise InvalidGenomeError(genome + " is not a valid genome")
        else: # call web api and populate the genome dict
            Genome.__populate_dicts(cls)
            if genome in Genome.__genome_dict:
                return Genome.__genome_dict[genome]
            else:
                raise InvalidGenomeError(genome + " is not a valid genome")

    def __populate_dicts(cls):
        """
            Helper method to populate the genome and organism dictionaries. 
            Client should not call this method!

            Calls endpoints:
                - GET /list/ucscGenomes
        """
        url = "http://api.genome.ucsc.edu/list/ucscGenomes"
        response = requests.get(url)
        info = response.json()
        for g,data in info['ucscGenomes'].items():
            instance = super().__new__(cls)
            instance.__chromosomes = []
            instance.__genome = g 
            Genome.__genome_dict[g] = instance
            org = data["organism"].lower()
            if org in Genome.__organism_dict:
                Genome.__organism_dict[org].append(g)
            else:
                Genome.__organism_dict[org] = [g]

    def __download_chrom_sequence(self, file_prefix, chromosome):
        """
            Helper method to get the entire DNA sequence for a specific chromsome in a UCSC database genome
            Saves to a created file with name file_prefix_{genome}_chromosome
            Client should not call the method!
            
            Params: 
                file_prefix (string): identifier for the file(s) where the sequence data should be dumped
                chromosome (string): optional parameter for which chromosome to download sequence data for

            Calls endpoints:
                - GET /getData/sequence?genome={genome};chrome={chromosome}

            Raises: InvalidChromosomeError if the chromosome does not exist for the genome
        """
        url = "http://api.genome.ucsc.edu/getData/sequence?genome="
        url += self.__genome + ";chrom="
        url += chromosome
        response = requests.get(url)
        info = response.json()
        
        if response.status_code in [200, 201, 202, 204]:
            with open(file_prefix + "_" + self.__genome + "_" + chromosome, "w", encoding='utf-8') as f:
                f.write(info['dna'])
                f.close()

        elif response.status_code == 400:
            raise InvalidChromosomeError("could not find chromosome " + chromosome + " in genome")

    def download_sequence(self, file_prefix, chromosome=None):
        """
            Downloads a DNA sequence of a given chromosome for a genome
            If no chromosome is given, download all chromosomes of that genome
            Sequences are outputted to a created file with path file_prefix_{genome}_{chromosome}
            One file per downloaded chromosome is created
            
            Params:
                file_prefix (string): identifier for the file(s) where the sequence data should be dumped
                chromosome (string): optional parameter for which chromosome to download sequence data for
            
            Returns:
                file(s): file object(s) containing the DNA sequence of the chromosome(s)

            Raises: InvalidChromosomeError if the input chromosome does not exist for the genome
        """
        if chromosome == None:
            chromosomes = self.list_chromosomes()
            for chrom in chromosomes: 
                self.__download_chrom_sequence(file_prefix, chrom)
        else:
            self.__download_chrom_sequence(file_prefix, chromosome)
    
    def list_chromosomes(self):
        """
            Lists all chromosomes for a genome

            Calls endpoints:
                -GET /list/chromosomes?genome={genome}

            Returns:
                string: list of chromosomes for a genome
        """
        # lazily populates chromosomes for the genome, only fetches once
        if len(self.__chromosomes) == 0:
            url = "http://api.genome.ucsc.edu/list/chromosomes?genome="
            url += self.__genome
            response = requests.get(url)
            info = response.json()
            chromosome_list = []
            for chromosome in info["chromosomes"]:
                chromosome_list.append(chromosome)
            self.__chromosomes = chromosome_list
        return self.__chromosomes
       
    def list_genomes(organism=None):
        """
            Static utility method
            If organism is not specified, lists all genomes in the UCSC database
            If organism specified, lists all genomes corresponding to that organism
            
            Params:
                organism (string): optional string to specify which organism to get the genomes for

            Returns:
                List[string]: list of genomes

            Raises:
                InvalidOrganismError: If there is no corresponding genome to the organism in the UCSC genome database

        """
        if organism == None:
            if len(Genome.__genome_dict) == 0:
                Genome.__populate_dicts(Genome)
            return Genome.__genome_dict.keys()
        else:
            if organism.lower() in Genome.__organism_dict:
                return Genome.__organism_dict[organism.lower()]
            else:
                raise InvalidOrganismError(organism + " is not a valid organism")


