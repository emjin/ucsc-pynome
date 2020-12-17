# UCSC Pynome

 A Python UCSC Genome Browser Library
 
## Support
 
 Provides programmatic support for downloading sequence data from genomes, chromosomes, and specific coordinates as well as the liftover functionality on sets of sequences (usually contained within BED files). This API also provides object representation of concepts (such as genomes and sequences) for easier and less error-prone usage of the UCSC Genome Browser.
 
## Installation
 
### Mac OS Users
If you encounter a "liftOver can’t be opened because the identity of the developer cannot be confirmed", run the ['setup script'](/ucscpynome/setup.sh) before running any code.

### Other platforms
Go to http://hgdownload.soe.ucsc.edu/admin/exe/ and download the binary for your running platform. Replace the liftOver executable in ucscpynome with the downloaded one and run `chmod +x liftOver`.

## Usage

UCSC Pynome can be used to download sequences and liftover coordinates. It contains three submodules: Genome, Sequence, and SequenceSet.

The Genome class is used to get top level data. For example, it is possible to list all the genomes available in the UCSC database:

```
print(Genome.list_genomes())
```

It is also possible to download an entire genome or an entire chromosome from the browser. For example, the following code downloads the sequences of a list of mammals into a folder called "mammals", excluding chromosomes such as chrUn_XXX.

```
mammals = ["bosTau9", "canFam4", "choHof1", "dasNov3", "dipOrd1", "echTel1"]

for mammal in mammals:
    Genome.download_sequence(Genome(mammal), "mammals/", include_pseudochromosomes=False)
```

The SequenceSet class operates on lists of sequences. A SequenceSet is created using a bed file and an alignment name, and may be outputted as a bed file of coordinates or a fasta file of its sequences.

For example, the following code pulls a gene, specified by gene.bed, and its orthologs in several species.

```
hg38_gene = SequenceSet(["gene.bed"], "hg38")
primates = ["panTro6", "ponAbe3", "rheMac10"]

for primate in primates:
    primate_gene = SequenceSet.liftover(hg38_gene, primate)
    primate_gene.to_fasta("genes/" + primate + "_gene.fasta")

hg38_gene.to_fasta("gene.fasta")
```

The SequenceSet class has the mutable field sequences, which is a list of Sequence objects.

Each Sequence object is specified by its coordinates. A sequence class lets you get and output the chromosome, start, end, and genome of a sequence, as well as the sequence string. For example:

```        
newSeq = Sequence(1234567, 1234589, "hg38", "chr2")
print("chromosome: " + newSeq.chromosome() + )
```

## Examples

See [`example-workspace/new_api/`](/example-workspace/new_api) for examples of how to use this API.







