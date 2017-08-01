#!/bin/sh
simu=$1
outdir=$2
python scripts/cleanup.py ${outdir}/${simu}/${simu} ${outdir}/${simu}/normal
