#!/bin/sh
javasim_libdir=$1
javasim_bindir=$2
ref=$3
out=$4

java -cp ${javasim_libdir}/commons-lang3-3.1.jar:${javasim_libdir}/sam-1.77.jar:${javasim_libdir}/picard-1.77.jar:${javasim_bindir} ReferenceSimulation $ref ${out}.fa
