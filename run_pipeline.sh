#!/bin/sh

config=$1
name=$2
echo "running "$name
rubra sv_simu_pipe.py --config $config --style run
