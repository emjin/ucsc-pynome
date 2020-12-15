import requests
import re


class NetworkError(Exception):
    pass 

class BadRequestError(Exception):
    pass

class Sequence():
    """Represents a DNA sequence of a chromosome in a UCSC database genome characterized by start and end coordinates.

    Use methods here to get the string value of a certain sequence.
    
    Raises:
        NetworkError:  raised if a connection issue occurs during the API request
        BadRequestError: if a 400 status code is returned due to incorrect genome, chromosome or coordinates given. 
                         Specifics will be printed out with the error
    """ 
    def __init__(self, start, end, genome, chromosome, label=None):
        """ Get an instance of a Sequence. Client should not use the constructor!

        Args: 
            start (int): start coordinate of the sequence
            end (int): int coordinate of the sequence
            genome (string): target genome
            chromosome (string): target chromosome
            label (string): optional string for the user to identify the Sequence by
        """
        self.start = start
        self.end = end
        self.genome = genome 
        self.chromosome = chromosome
        self.label = label
        self.__sequence = None

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
            "genome": self.genome,
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
        url += 'genome=' + self.genome + ';'
        url += 'chrom=' + self.chromosome + ';'
        url += 'start=' + str(self.start) + ';'
        url += 'end=' + str(self.end)
        response = requests.get(url)
        info = response.json()
        
        if response.status_code in [200, 201, 202, 204]:
            return info['dna']

        elif response.status_code == 400:
            error_msg = info['error']
            new_error_msg = re.sub('for endpoint \'.*(,|$)', '', error_msg).rstrip()
            raise BadRequestError(new_error_msg)

        else:
            raise NetworkError('%d', response.status_code)
