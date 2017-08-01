#!/bin/sh
'''
Generate config file given template
'''
import argparse
import csv

parser = argparse.ArgumentParser(prefix_chars='--')
parser.add_argument("config_file")
parser.add_argument("variant_type")
parser.add_argument("purity")
parser.add_argument("coverage")
args = parser.parse_args()

config_file = args.config_file
variant_type = args.variant_type
purity = args.purity
cov = args.coverage
tum_cov = int( float(cov) * (float(purity) / 100) )
norm_cov = int( float(cov) * (1 - (float(purity) / 100)))

output = []
with open(config_file, 'r') as cf:
    for line in cf:
        if line.startswith('tumour_outname'):
            line = line.strip().split('=')[0]
            line = line + '= "tumour_p%s_%s"\n' % (purity, variant_type)
        elif line.startswith('weights'):
            line = line.strip().split('=')[0]
            line = line + '= "%s=1.0"\n' % variant_type.lower()
        elif line.startswith('tumour_cov'):
            line = line.strip().split('=')[0]
            line = line + '= %d\n' % tum_cov
        elif line.startswith('norm_cov'):
            line = line.strip().split('=')[0]
            line = line + '= %d\n' % norm_cov
        output.append(line)

output_config = 'c%s_p%s_%s_config.py' % (cov, purity, variant_type)
with open(output_config, 'w') as oc:
    for row in output:
        oc.write(row)
