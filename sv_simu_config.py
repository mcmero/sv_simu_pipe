# directory variables
ref_genome          = "reference/12" #where .fa and .fa.fai are the fasta and indexes respectively
simseq_dir          = "SimSeq"
repeat_masker_file  = "reference/hg19_repeats.txt"
simu_outdir         = "simu_out"
javasim_libdir      = "refpluspipeline/reference_generation/lib"
javasim_bindir      = "refpluspipeline/reference_generation/bin"
normal_outname      = "normal"
tumour_outname      = "tumour_p100_INV"
weights             = "del=1.0"
threads             = 8
aligner             = "bwa"

# simulated tumour clone parameters
read_len            = 100
frag_len            = 300
frag_std            = 20
chrom_len           = 133851894 #in this case, chrom 12 len
tumour_cov          = 50
norm_cov            = 0
sv_interval         = 100000 # create one SV per X bp interval

test_mode           = "false"
pipeline            = {
    "logDir": "log_pipe",
    "logFile": "sv_simu_pipe.log",
    "style": "print",
    "procs": 1,
    "verbose": 1,
    "end": ["generate_variants","variants_to_bed",\
            "generate_normal_reads","generate_tumour_reads",
            "tumour_index"],
    "force": [],
    "rebuild": "fromstart",
    "restrict_samples": False,
}
stageDefaults = {
    "distributed": False,
#    "walltime": "16:00:00",
#    "memInGB": 16,
#    "queue": "batch",
#    "account": "VR0002",
#    "modules": ["java","python-gcc",
#                "intel","bowtie2-intel/2.2.4",
#                "samtools-intel/0.1.19"], 
}
stages = {
    "generate_variants": {
        "command": "java -cp %javasim_bindir VariationRandomization %ref_seq_index %interval %out hom %weights",
    },
    "simulate_variants": {
        "command": "scripts/refsim.sh %javasim_libdir %javasim_bindir %fasta %out",
    },
    "variants_to_bed": {
        "command": "scripts/variants_to_bed.sh %variants %bedout",
    },
    "generate_reads_simseq": {
        "command": "time scripts/simseq.sh %simseq_dir %libdir %read_len %frag_len %frag_std %fasta_ref %reads %outdir",
    },
    "create_tumour_mixture": {
        "command": "scripts/create_tumour_mixture.sh %tumour_base %norm_base %mix_base"
    },
    "align_tumour_reads_bowtie": {
        "command": "bowtie2 --local -p %threads -x %ref_seq_file -1 %fastq_r1 -2 %fastq_r2 -S %outsam --rg-id %tumour_rg --rg SM:%tumour_sm",
    },
    "align_tumour_reads_bwa": {
        "command": "bwa mem -t %threads %ref_seq_file %fastq_r1 %fastq_r2 -R %rg_header > %outsam",
    },
    "tumour_sam_to_bam": {
        "command": "sam=%tumour_sam ; bam=%tumour_bam ; samtools view -bS $sam -o $bam",
    },
    "tumour_sort_bam": {
        "command": "samtools sort %bam -o %out_prefix",
    },
    "tumour_index": {
        "command": "samtools index %bam",
    },
    "cleanup": {
        "command": "python scripts/cleanup.py %tumour_base_name %norm_base_name",
    },
}
