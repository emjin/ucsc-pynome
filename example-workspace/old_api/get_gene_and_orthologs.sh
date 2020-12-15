#!/usr/local/bin/bash

# note: this does not fully work; it doesn't process the output but just leaves it as it's downloaded
# we felt that, given the other solution is fourteen lines, that this adequately demonstrated how our
# wrapper simplified the process

# create file for coords
hchr="chr3"
hstart="70954708"
hend="71583728"
echo -e "${hchr}\t${hstart}\t${hend}" > gene_files/hg38_gene.bed

# download human sequence
wget -O "gene_files/hg38_gene" "https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=${hchr};start=${hstart};end=${hend}" 

src=hg38
genomes=("panTro6" "ponAbe3" "rheMac10")
for genome in ${genomes[@]}; do
   # get chain file (overwrite original if necessary)
   genome_upper=${genome^}
   liftover="${src}To${genome_upper}.over.chain"
   wget -O "liftover_files/${liftover}.gz" "https://hgdownload.cse.ucsc.edu/goldenpath/${src}/liftOver/${liftover}.gz"
   gunzip "liftover_files/${liftover}.gz"

   # liftover coordinates
   lifted_coord_file="gene_files/${genome}_gene.bed"
   touch $lifted_coord_file
   ../../ucscpynome/liftOver gene_files/hg38_gene.bed "liftover_files/${liftover}" $lifted_coord_file unmapped.bed

   # get coordinates from bed file
   while IFS= read -r line
   do
     coords=($line)
     chr=${coords[0]}
     start=${coords[1]}
     end=${coords[2]}
     seq_entrypoint="https://api.genome.ucsc.edu/getData/sequence?genome=${genome};chrom=${chr};start=${start};end=${end}"
     wget -O "gene_files/${genome}_gene" seq_entrypoint
   done < "$lifted_coord_file"
done