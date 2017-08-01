#!/bin/sh

########################################################
#Generate simulation config files and run pipeline
########################################################

cov=50

for type in DEL DUP INV TRX; do
    for purity in 100 80 60 40 20; do

        # generate config file
        python generate_config.py sv_simu_config.py $type $purity $cov

        # run pipeline
        ./run_pipeline.sh c${cov}_p${purity}_${type}_config.py c${cov}_p${purity}_${type}

    done
done
