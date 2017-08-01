#!/bin/sh
fasta=$1
out=$2
awk '{FS="\t"}{split($2,x,":")}{split(x[2],y,"-")}{print x[1]"\t"y[1]"\t"y[2]"\t"$1}' $fasta > $out
