# UCSC Pynome

 A Python UCSC Genome Browser Library
 
## Support
 
 Provides programmatic support for downloading sequence data from genomes, chromosomes, and specific coordinates as well as the liftover functionality on sets of sequences (usually contained within BED files). This API also provides object representation of concepts (such as genomes and sequences) for easier and less error-prone usage of the UCSC Genome Browser.
 
## Usage
 
### Mac OS Users
If encounter a "liftOver can’t be opened because the identity of the developer cannot be confirmed", run the ['setup script'](/ucscpynome/setup.sh) before running any code.

### Other platforms
Go to http://hgdownload.soe.ucsc.edu/admin/exe/ and download the binary for your running platform. Replace the liftOver executable with the downloaded one and run `chmod +x liftOver`.

## Examples

See [`example-workspace/new_api/`](/example-workspace/new_api) for examples of how to use this API.







