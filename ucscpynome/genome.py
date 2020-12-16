import sys
import subprocess
import os.path
from os import path
import gzip
import requests
from .retry import Requests


class InvalidGenomeError(ValueError):
    """ InvalidGenomeError is raised when the user inputs an invalid genome """
    pass

class InvalidChromosomeError(ValueError):
    """ InvalidChromosomeError is raised when the user inputs an invalid chromosome """
    pass

class InvalidOrganismError(ValueError):
    """ InvalidOrganismError is raised when the user inputs an invalid organism """
    pass

class LiftoverError(ValueError):
    pass

class Genome():
    """ 
        An instance of Genome represents a genome. Each unique genome only has one
        genome object associated with it. Genomes are equivalent if they represent the
        same genome. A genome object allows users to easily access different 
        functionalities related to the genome. The Genome class also contains utility 
        methods common across all genomes.

        Raises:
        InvalidGenomeError
        InvalidChromosomeError
        InvalidOrganismError
    """
    __genome_request = Requests()
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

    def __str__(self):
        return self.__genome

    def __download_chrom_sequence(self, file_prefix, chromosome):
        """
            Helper method to get the entire DNA sequence for a specific chromsome in a 
            UCSC database genome.
            Saves to a created file with name file_prefix_{genome}_chromosome
            Client should not call the method!
            
            Params: 
                file_prefix (string): identifier for the file(s) where the sequence data 
                should be dumped
                chromosome (string): optional parameter for which chromosome to download 
                sequence data for

            Calls endpoints:
                - GET /getData/sequence?genome={genome};chrome={chromosome}

            Raises: InvalidChromosomeError if the chromosome does not exist for the genome
        """
        print("Downloading sequence for chromosome " + chromosome + " in genome " + self.__genome)
        url = "http://api.genome.ucsc.edu/getData/sequence?genome="
        url += self.__genome + ";chrom="
        url += chromosome
        response = Genome.__genome_request.get(url)
        info = response.json()

        if response.status_code in [200, 201, 202, 204]:
            with open(file_prefix + "_" + self.__genome + "_" + chromosome, "w", encoding='utf-8') as f:
                f.write(info['dna'])
                f.close()
            print("Download complete for chromosome " + chromosome + " in genome " + self.__genome)

        elif response.status_code == 400:
            raise InvalidChromosomeError("could not find chromosome " + chromosome + " in genome")

    def download_sequence(self, file_prefix=None, chromosome=None):
        """
            Downloads a DNA sequence of a given chromosome for a genome
            If no chromosome is given, download all chromosomes of that genome
            Sequences are outputted to a created file with path :
            file_prefix_{genome}_{chromosome}
            One file per downloaded chromosome is created

            Timeout and retries and be set in set_timeout and set_retries
            Default: 600 seconds, 2 retries
            
            Params:
                file_prefix (string): identifier for the file(s) where the sequence data 
                should be dumped
                chromosome (string): optional parameter for which chromosome to download 
                sequence data for
            
            Returns:
                file(s): file object(s) containing the DNA sequence of the chromosome(s)

            Raises: InvalidChromosomeError if the input chromosome does not exist for the 
                    genome
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
       
    @staticmethod
    def list_genomes(organism=None):
        """
            Static utility method
            If organism is not specified, lists all genomes in the UCSC database
            If organism specified, lists all genomes corresponding to that organism
            
            Params:
                organism (string): optional string to specify which organism to get the 
                genomes for

            Returns:
                List[string]: list of genomes

            Raises:
                InvalidOrganismError: If there is no corresponding genome to the organism 
                in the UCSC genome database

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

    @staticmethod
    def liftover(src_genome, target_genome, src_file, target_file, 
                 unmapped_file = None, path_to_chain = None):
        """
            Static utility method to perform liftover between two genomes.
            Wrapper around UCSC's command-line liftOver tool.

            This method generates and saves additional files when necessary: 

            log file (always): 
                {src_genome}To{target_genome}_liftover_log.err

            chain files (if not specified):
                {src_genome}To{Target_genome}.over.chain.gz
                {src_genome}To{Target_genome}.over.chain

            unmapped file (if not specified):
                {src_genome}To{target_genome}_unmapped.bed


            This method saves all generated files inside /liftover_files directory, which
            has three subdirectories:

            /bed_files      : any bed files created by ucscpynome in the process of liftover,
                              including unmapped.bed files.
            /chain_files    : chain files downloaded (when path_to_chain is not specified).
            /log_files      : logs generated by UCSC's liftOver tool
  
            Params:
                src_genome (Genome): genome to liftover from
                target_genome (Genome): genome to liftover to
                src_file (string): path to source genome's bed file
                target_file (string): path to bed file to write the lifted genome data
                unmapped_file (string): optional parameter to specify the path to a bed 
                file to store unmapped coordinates
                path_to_chain (string): optional parameter to specify the path to a
                custom chain file to use for the liftover

            Raises:
                LookupError: If the chain file for the specified source and target 
                genomes doesn't exist.
                LiftoverError: If there is an error during liftover using UCSC's 
                command-line liftover tool.

        """

        VALID_LOG_LINES = ["Reading liftover chains", "Mapping coordinates"]
        CHAIN_FILES_PATH = "liftover_files/chain_files/"
        LOG_FILES_PATH = "liftover_files/log_files/"
        BED_FILES_PATH = "liftover_files/bed_files/"

        script_dir = os.path.dirname(__file__)
        
        def check_liftover_success(liftover_log):
            liftover_file = open(liftover_log, 'r')
            lift_err_msg = ""
            for line in liftover_file:
                line = line.strip()
                if line not in VALID_LOG_LINES:
                    lift_err_msg += "liftover error: " + line + "\n"
            liftover_file.close()
            return lift_err_msg

        def download_chain_file(chain_name, url, redownload):
            # path_to_chain = CHAIN_FILES_PATH + chain_name
            path_to_chain = os.path.join(script_dir, CHAIN_FILES_PATH + chain_name)
            
            path_to_gz = path_to_chain + '.gz'

            if redownload or (not path.exists(path_to_chain) and not path.exists(path_to_gz)):
                r = requests.get(url, allow_redirects=True)
                if r.status_code != 200:
                    raise LookupError("Chain file " + chain_name + " does not exist. There may not be a valid mapping between these genomes")

                gzip.open(path_to_gz, 'wb').write(r.content)

            if redownload or not path.exists(path_to_chain):
                content = gzip.open(path_to_gz, 'rb').read()
                f = open(path_to_chain, 'wb')
                chain_contents = gzip.decompress(content)
                f.write(chain_contents)
                f.close()

            return path_to_chain

        # get genome names for source and target
        src = str(src_genome)
        target = str(target_genome)

        # if unmapped_file not given, create a new one
        if not unmapped_file:
            unmapped_file = os.path.join(script_dir, BED_FILES_PATH + src + "To" + target + "_unmapped.bed")

        # create a liftover log file
        liftover_log = os.path.join(script_dir, LOG_FILES_PATH + src + "To" + target + "_liftover_log.err")

        # download chain file if necessary
        chainprovided = True
        if not path_to_chain:
            chainprovided = False
            capitalized_target = target[0].capitalize() + target[1:]
            chain_name = src + 'To' + capitalized_target + '.over.chain'
            url = 'https://hgdownload.cse.ucsc.edu/goldenpath/' + src + '/liftOver/' + chain_name + '.gz'
            path_to_chain = download_chain_file(chain_name, url, redownload=False)

        # make a call to liftover command-line tool
        liftover_call = 'liftOver ' + src_file + ' ' + path_to_chain + ' ' + target_file + ' ' + unmapped_file
        redirect = ' 2> ' + liftover_log
        os.system(os.path.join(script_dir, liftover_call) + redirect)

        # handle errors
        lift_err_msg = check_liftover_success(liftover_log)

        # error handling
        liftover_error = False
        if lift_err_msg:
            if not chainprovided:
                # retry upon failure
                download_chain_file(chain_name, url, redownload=True)
                os.system(liftover_call + redirect)
                lift_err_msg = check_liftover_success(liftover_log)
                if lift_err_msg: 
                    lift_err_msg += "Error while lifting over from " + src + " to " + target + "\n"
                    lift_err_msg += "The chain file downloaded from " + url + " may be invalid\n"
                    lift_err_msg += "If the chain file is valid, please file an issue"
                    liftover_error = True
            else:
                lift_err_msg += "Error while lifting over from " + src + " to " + target + "\n"
                lift_err_msg += "The chain file " + path_to_chain + " may be invalid"
                liftover_error = True
                
        if liftover_error:
            raise LiftoverError(lift_err_msg)


    def set_timeout(timeout):
        """ 
            Sets the Genome class request timeout for download_sequence

            Default: 600 seconds

            Params:
                timeout (int):  new timoout duration in seconds 

        """
        Genome.__genome_request.set_timeout(timeout)

    def set_retries(retries):
        """ 
            Sets the Genome class request number of retries for download_sequence

            Default: 2 tries

            Params:
                retries (int):  new number of request retries 

        """
        Genome.__genome_request.set_retries(retries)







