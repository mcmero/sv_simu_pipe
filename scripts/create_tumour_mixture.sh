#!/bin/sh

tumour_base=$1
norm_base=$2
mix_base=$3

cat ${tumour_base}_R1.fq ${norm_base}_R1.fq > ${mix_base}_R1.fq
cat ${tumour_base}_R2.fq ${norm_base}_R2.fq > ${mix_base}_R2.fq
