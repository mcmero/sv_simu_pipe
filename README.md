# README #

### SV simulation pipeline ###

Simulates SV of different purity levels and types. This was used to generate test data for validating the read counting used in [SVclone](https://github.com/mcmero/SVclone).

### How do I get set up? ###

Install these dependencies:

* [Java Development Kit](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)
* [Samtools](http://samtools.sourceforge.net/) -- make sure samtools is in your $PATH
* [Rubra](https://github.com/bjpop/rubra.git) -- install Rubra

These instructions will clone this repository, and install [SimSeq](https://github.com/jstjohn/SimSeq) and [refpluspipeline](https://github.com/mcmero/refpluspipeline).

    git clone git@github.com:mcmero/sv_simu_pipe.git
    cd sv_simu_pipe

    git clone git@github.com:mcmero/refpluspipeline.git
    cd refpluspipeline
    ./compile_javasim.sh

    cd ..
    git clone https://github.com/jstjohn/SimSeq.git

Create a reference directory under your sv_simu_pipe directory, and add the following files:

* [hg19 chromosome reference](http://hgdownload.cse.ucsc.edu/goldenpath/hg19/chromosomes/) (pick one chromosome, 12 is used in the example) -- generate an index with [Bowtie2](bowtie-bio.sourceforge.net/bowtie2/)
* [hg19 repeat track](https://genome.ucsc.edu/cgi-bin/hgTables) -- from UCSC (name it hg19_repeats.txt)

Configure the sv_simu_config.py configuration file, making sure the reference genome, repeats file, SimSeq dir and the directories for the java simulator are set correctly.  

### Running the pipeline ###

Run as:

    ./batch_simu.sh

This will generate 20 simulations: 20%, 40%, 60%, 80% and 100% purity mixtures for deletions, duplications, inversions and traslocations. This can be used as input for SV callers. VAFs can then be characterised using [SVclone](https://github.com/mcmero/SVclone).
