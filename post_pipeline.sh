#!/bin/sh

simu=$1

cd /vlsci/VR0211/shared/marek-working/Socrates
sbatch ./simu_run_soc.sh $simu

#cd /mnt/apps/sv_process
#./simu_sv_proc.sh $simu

#cd /mnt/apps/svclone
#./svclone.sh $simu
#cp $simu/${simu}_filtered_svs.tsv /mnt/storage/R/sv_simulation_analysis/data/ 
