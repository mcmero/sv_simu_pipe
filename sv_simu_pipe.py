#!/bin/env python
'''
Pipeline to automate simulation of tumour samples using svcnvsim 
'''

import re
import ipdb
import os
import subprocess
from os          import path
from ruffus      import *
from rubra.utils import pipeline_options
from rubra.utils import (runStageCheck,mkDir,splitPath)

simseq_dir          = pipeline_options.simseq_dir
normal_outname      = pipeline_options.normal_outname
simu_outdir         = pipeline_options.simu_outdir
tumour_outname      = pipeline_options.tumour_outname
javasim_libdir      = pipeline_options.javasim_libdir
javasim_bindir      = pipeline_options.javasim_bindir
simseq_dir          = pipeline_options.simseq_dir
threads             = pipeline_options.threads
aligner             = pipeline_options.aligner

read_len            = pipeline_options.read_len
frag_len            = pipeline_options.frag_len
frag_std            = pipeline_options.frag_std
tumour_cov          = pipeline_options.tumour_cov
norm_cov            = pipeline_options.norm_cov
sv_interval         = pipeline_options.sv_interval
chrom_len           = pipeline_options.chrom_len
outdir              = '%s/%s' % (simu_outdir,tumour_outname)
weights             = pipeline_options.weights
ref_genome          = pipeline_options.ref_genome
ref_fasta           = '%s.fa' % ref_genome
ref_index           = '%s.fai' % ref_fasta
    
normal_reads        = (chrom_len/frag_len) * (norm_cov + int((tumour_cov/2)))
tumour_reads        = (chrom_len/frag_len) * int((tumour_cov/2))

if not path.exists(outdir):
    os.makedirs(outdir)

with open('%s/parameters.txt' % outdir, "w") as outf:
    expected_vaf = tumour_reads/float(normal_reads + tumour_reads)
    params = map(str,[ref_genome, read_len, frag_len,frag_std, sv_interval, tumour_cov, 
                      norm_cov, tumour_reads, normal_reads, expected_vaf])
    params = '\t'.join(params)
    outf.write("ref_genome\tread_len\tfrag_len\tfrag_std\tsv_interval\ttumour_cov\tnorm_cov\ntumour_reads\tnormal_reads\texpected_vaf\n")
    outf.write("%s\n" % params)

@transform(ref_index,  regex('.*\.fai'), \
           [r'%s/%s.fa'%(outdir,tumour_outname),r'%s/generate_variants.Success'%outdir])
def generate_variants(ref_index,outputs):
    fasta_out, flagFile = outputs
    runStageCheck('generate_variants', flagFile, javasim_bindir, ref_index, sv_interval, '%s/%s' % (outdir,tumour_outname), weights)

@transform(ref_fasta,  regex('(.*)\.fa'), \
        [r'%s/%s_R1.fq'%(outdir,normal_outname),r'%s/%s_R2.fq'%(outdir,normal_outname),r'%s/generate_normal_reads.Success'%outdir])
def generate_normal_reads(ref_fasta,outputs):
    fastq_r1, fastq_r2, flagFile = outputs
    normal_out = '%s/%s' % (outdir,normal_outname)
    cov = norm_cov + int((tumour_cov/2)) #create normal component assuming half the "tumour" is normal
    runStageCheck('generate_reads_simseq', flagFile, simseq_dir, javasim_libdir, read_len, frag_len, frag_std, ref_fasta, normal_reads, normal_out)

@transform(generate_variants, regex('(.*)\/([a-zA-Z0-9_\.]+)\.fa'), [r'\1/\2_variants.bed',r'\1/variants_to_bed.Success'])
def variants_to_bed(inputs,outputs):
    variant_fasta, _success = inputs
    variant_bed, flagFile = outputs
    runStageCheck('variants_to_bed',flagFile, variant_fasta, variant_bed)

@transform(generate_variants, regex('(.*)\/([a-zA-Z0-9_\.]+)\.fa'), [r'\1/\2.fa_reference.fa', r'\1/simulate_variants.Success'])
def simulate_variants(inputs,outputs):
    variant_fasta, _success = inputs
    fasta_out, flagFile = outputs
    match = re.search('(.*)\/([a-zA-Z0-9_\.]+)\.fa',variant_fasta)
    variant_fasta = '%s/%s' % (match.group(1),match.group(2))
    runStageCheck('simulate_variants', flagFile, javasim_libdir, javasim_bindir, ref_fasta, variant_fasta)

@transform(simulate_variants,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.fa_reference.fa'), \
        [r'\1/\2_R1.fq', r'\1/\2_R2.fq',r'\1/generate_tumour_reads.Success'])
def generate_tumour_reads(inputs,outputs):
    variant_fasta, _success = inputs
    fastq_r1, fastq_r2, flagFile = outputs

    match = re.search('(.*)\/([a-zA-Z0-9_\.]+)\.fa_reference.fa',variant_fasta)
    tumour_out = '%s/%s' % (match.group(1),match.group(2))
    cov = int(tumour_cov/2) #assume variants occur only on one chromosome
    
    # have to tweak tumour reads based on generated reference genome
    proc = subprocess.Popen(["wc",variant_fasta],stdout=subprocess.PIPE)
    wc_out = proc.stdout.readline().split()
    tum_chrom_len = int(wc_out[2])-4 #4 = number of characters in the fasta header
    tumour_reads = (tum_chrom_len/frag_len) * int((tumour_cov/2))

    runStageCheck('generate_reads_simseq', flagFile, simseq_dir, javasim_libdir, read_len, frag_len, frag_std, variant_fasta, tumour_reads, tumour_out)

@transform(generate_tumour_reads,  regex(r'(.*)\/([a-zA-Z0-9_\.]+)_R(1|2)\.fq'), [r'\1/pure_\2.sam', r'\1/align_pure_tumour_reads.Success'])
def align_pure_tumour_reads(inputs,outputs):
    fastq_r1, fastq_r2, _success = inputs
    samFile, flagFile = outputs
    outSam = '%s/pure_%s.sam' % (outdir,tumour_outname)
    if aligner=='bowtie':
        runStageCheck('align_tumour_reads_bowtie', flagFile, threads, ref_fasta, fastq_r1, fastq_r2, outSam, tumour_outname, tumour_outname)
    elif aligner=='bwa':
        tumour_rg = '"@RG\\tID:%s\\t@SM:%s"' % (tumour_outname, tumour_outname)
        runStageCheck('align_tumour_reads_bwa', flagFile, threads, ref_fasta, fastq_r1, fastq_r2, tumour_rg, outSam)
    else:
        raise ValueError('Invalid aligner specified!')

@transform(align_pure_tumour_reads,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.sam'), [r'\1/\2.bam', r'\1/pure_tumour_sam_to_bam.Success'])
def pure_tumour_sam_to_bam(inputs,outputs):
    samFile, _success = inputs
    bamFile, flagFile = outputs

    match = re.search('(.*)\.sam',samFile)
    bamFile = match.group(1) + '.bam'
    runStageCheck('tumour_sam_to_bam', flagFile, samFile, bamFile)

@transform(pure_tumour_sam_to_bam,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.bam'), [r'\1/\2.sorted.bam', r'\1/pure_tumour_sort_bam.Success'])
def pure_tumour_sort_bam(inputs,outputs):
    bamFile, _success = inputs
    sortBamFile, flagFile = outputs

    match = re.search('(.*)\.bam',bamFile)
    sortBamPrefix = match.group(1) + '.sorted.bam'
    runStageCheck('tumour_sort_bam', flagFile, bamFile, sortBamPrefix)

@transform(pure_tumour_sort_bam,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.bam'), [r'\1/\2.bam.bai', r'\1/pure_tumour_index_bam.Success'])
def pure_tumour_index(inputs,outputs):
    bamFile, _success = inputs
    index, flagFile = outputs

    runStageCheck('tumour_index', flagFile, bamFile)

@follows(generate_normal_reads)
@transform(generate_tumour_reads, regex(r'(.*)\/([a-zA-Z0-9_\.]+)_R(1|2)\.fq'), \
         [r'\1/\2_mixture_R1.fq', r'\1/\2_mixture_R2.fq', r'\1/create_tumour_mixture.Success'])
def create_tumour_mixture(inputs,outputs):
    fastq_r1, fastq_r2, _success = inputs
    mix_r1, mix_r2, flagFile = outputs

    match       = re.search(r'(.*)\/([a-zA-Z0-9_\.]+)_R(1|2)\.fq', fastq_r1)
    tumour_base = '%s/%s' % (match.group(1),match.group(2))
    norm_base   = '%s/%s' % (outdir,normal_outname)
    mix_base  = '%s/%s_mixture' % (match.group(1),match.group(2))

    runStageCheck('create_tumour_mixture', flagFile, tumour_base, norm_base, mix_base)

@transform(create_tumour_mixture,  regex(r'(.*)\/([a-zA-Z0-9_\.]+)_mixture_R(1|2)\.fq'), [r'\1/\2.sam', r'\1/align_tumour_reads.Success'])
def align_tumour_reads(inputs,outputs):
    fastq_r1, fastq_r2, _success = inputs
    samFile, flagFile = outputs
    outSam = '%s/%s.sam' % (outdir,tumour_outname)
    if aligner=='bowtie':
        runStageCheck('align_tumour_reads_bowtie', flagFile, threads, ref_fasta, fastq_r1, fastq_r2, outSam, tumour_outname, tumour_outname)
    elif aligner=='bwa':
        tumour_rg = '"@RG\\tID:%s\\t@SM:%s"' % (tumour_outname, tumour_outname)
        runStageCheck('align_tumour_reads_bwa', flagFile, threads, ref_fasta, fastq_r1, fastq_r2, tumour_rg, outSam)
    else:
        raise ValueError('Invalid aligner specified!')

@transform(align_tumour_reads,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.sam'), [r'\1/\2.bam', r'\1/tumour_sam_to_bam.Success'])
def tumour_sam_to_bam(inputs,outputs):
    samFile, _success = inputs
    bamFile, flagFile = outputs

    match = re.search('(.*)\.sam',samFile)
    bamFile = match.group(1) + '.bam'
    runStageCheck('tumour_sam_to_bam', flagFile, samFile, bamFile)

@transform(tumour_sam_to_bam,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.bam'), [r'\1/\2.sorted.bam', r'\1/tumour_sort_bam.Success'])
def tumour_sort_bam(inputs,outputs):
    bamFile, _success = inputs
    sortBamFile, flagFile = outputs

    match = re.search('(.*)\.bam',bamFile)
    sortBamPrefix = match.group(1) + '.sorted.bam'
    runStageCheck('tumour_sort_bam', flagFile, bamFile, sortBamPrefix)

@transform(tumour_sort_bam,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.bam'), [r'\1/\2.bam.bai', r'\1/tumour_index_bam.Success'])
def tumour_index(inputs,outputs):
    bamFile, _success = inputs
    index, flagFile = outputs

    runStageCheck('tumour_index', flagFile, bamFile)

@transform(tumour_index,  regex('(.*)\/([a-zA-Z0-9_\.]+)\.bam\.bai'), r'\1/cleanup.Success')
def cleanup(inputs,outputs):
    bamIndex, _success = inputs
    flagFile = outputs

    tumour_base_name = '%s/%s' % (outdir,tumour_outname)
    normal_base_name = '%s/%s' % (outdir,normal_outname)
    
    runStageCheck('cleanup', flagFile, tumour_base_name, normal_base_name)

