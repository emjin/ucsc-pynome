import requests
import re

class NetworkError(Exception):
    pass 

class BadRequestError(Exception):
    pass

class Sequence():
    def __init__(self, start, end, genome, chromosome, label=None):
        self.start = start
        self.end = end
        self.genome = genome 
        self.chromosome = chromosome
        self.label = label
        self.__sequence = None

    def string(self):
        if self.__sequence is None:
            self.__sequence = self.__get_sequence()
        return self.__sequence
 
    def __get_sequence(self):  
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

# newSeq = Sequence(1234, 5678, "hg38", "chrM") 
# print(newSeq.string())
