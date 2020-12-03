import sys
import subprocess
import requests
import os.path
from os import path

# testing
src = "hg19"
target = "hg38"
filename = "test_files/hg19_ex.bed"
outfile = "test_files/hg38_ex.bed"
unmapped_file = "unmapped.bed"

# code
chain_name = src + 'To' + target.capitalize() + '.over.chain'
url = 'https://hgdownload.cse.ucsc.edu/goldenpath/' + src + '/liftOver/' + chain_name + '.gz'
path_to_chain = 'liftover_files/' + chain_name
path_to_gz = path_to_chain + '.gz'

if not path.exists(path_to_chain) and not path.exists(path_to_gz):
    r = requests.get(url, allow_redirects=True)
    open(path_to_gz, 'w').write(r.content)
if not path.exists(path_to_chain):
    os.system('gunzip ' + path_to_gz)

liftover_call = './liftOver ' + filename + ' ' + path_to_chain + ' ' + outfile + ' ' + unmapped_file
redirect = ' 2> log.err'
os.system(liftover_call + redirect)

# If we want wget instead of downloading from internet
# wget --timestamping 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz')
