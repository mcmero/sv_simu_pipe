#!/bin/sh
simseq_dir=$1
libdir=$2
rlen=$3
flen=$4
std=$5
ref=$6
reads=$7
output=$8

java -jar -Xmx28g ${simseq_dir}/SimSeqNBProject/store/SimSeq.jar -1 $rlen -2 $rlen --error ${simseq_dir}/examples/hiseq_mito_default_bwa_mapping_mq10_1.txt --error2 ${simseq_dir}/examples/hiseq_mito_default_bwa_mapping_mq10_2.txt -l $flen -s $std --read_number $reads -r $ref -o $output.sam -u 0.01

java -jar -Xmx28g ${libdir}/picard.jar SamToFastq I=$output.sam FASTQ=${output}_R1.fq F2=${output}_R2.fq VALIDATION_STRINGENCY=SILENT; #rm -rf ${output}.sam
