import requests
import re
from . import Requests


class NetworkError(Exception):
    pass 

class BadRequestError(Exception):
    pass

class Sequence():
    """Represents a DNA sequence of a chromosome in a UCSC database genome characterized by start and end coordinates.

    Use methods here to get the string value of a certain sequence.

    Attributes:
        Read-only:
            start (int): Start index in chromosome
            end (int): End index in chromosome
            genome (Genome): Genome object to which sequence belongs
            chromosome (str): Chromosome to which sequence belongs
        Mutable:
            label (str): Additional metadata about sequence (read from bed file)
                         The user can change this at their discretion, e.g. if doing liftover
    
    Raises:
        NetworkError:  raised if a connection issue occurs during the API request
        BadRequestError: if a 400 status code is returned due to incorrect genome, chromosome or coordinates given. 
                         Specifics will be printed out with the error
    """ 

    __sequence_request = Requests()

    def __init__(self, start, end, genome, chromosome, label=None):
        """ Get an instance of a Sequence. Client should not use the constructor!

        Args: 
            start (int): start coordinate of the sequence
            end (int): int coordinate of the sequence
            genome (Genome): Genome object of the target genome
            chromosome (string): target chromosome
            label (string): optional string for the user to identify the Sequence by
        """
        self._start = start
        self._end = end
        self._genome = genome 
        self._chromosome = chromosome
        self.label = label
        self.__sequence = None

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end
    
    @property
    def genome(self):
        return self._genome

    @property
    def chromosome(self):
        return self._chromosome

    def string(self):
        """
        Gets DNA sequence of the chromsome in a UCSC database genome

        Returns: 
            string: DNA sequence of the Sequence() object 
        """
        if self.__sequence is None:
            self.__sequence = self.__get_sequence()
        return self.__sequence

    def __str__(self):
        """ Returns the Sequence info """
        info = {
            "start": self.start,
            "end": self.end,
            "genome": str(self.genome),
            "chromosome": self.chromosome
        }
        if self.label is not None:
            info["label"] = self.label
        return str(info)
        
 
    def __get_sequence(self):  
        """ Helper method to retrieve the DNA sequence from the specified chromosome in UCSC database genome.
        Clients should not use this method!

        Raises:
            BadRequestError
            NetworkError

        Calls endpoints:
            - GET /getData/sequence?/genome={genome};chrom={chromosome};start={start};end={end}
        """
        url = 'https://api.genome.ucsc.edu/getData/sequence?'
        url += 'genome=' + str(self.genome) + ';'
        url += 'chrom=' + self.chromosome + ';'
        url += 'start=' + str(self.start) + ';'
        url += 'end=' + str(self.end)
        response = Sequence.__sequence_request.get(url)
        info = response.json()
        
        if response.status_code in [200, 201, 202, 204]:
            return info['dna']

        elif response.status_code == 400:
            error_msg = info['error']
            new_error_msg = re.sub('for endpoint \'.*(,|$)', '', error_msg).rstrip()
            raise BadRequestError(new_error_msg)

        else:
            raise NetworkError('%d', response.status_code)

    def set_timeout(timeout):
        """ 
            Sets the Sequence class request timeout

            Params:
                timeout (int):  new timeout duration in seconds 

        """
        Sequence.__sequence_request.set_timeout(timeout)

    def set_retries(retries):
        """ 
            Sets the Sequence class request number of retries

            Params:
                retries (int):  new number of request retries 

        """
        Sequence.__sequence_request.set_retries(retries)