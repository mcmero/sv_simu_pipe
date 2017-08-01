#!/bin/env python

import argparse
import os
from os import path

parser = argparse.ArgumentParser()
parser.add_argument(dest="tumour_base_name")
parser.add_argument(dest="normal_base_name")

args = parser.parse_args()
tumour_base = args.tumour_base_name
norm_base = args.normal_base_name

tumour_bam = "%s.sorted.bam" % tumour_base
tumour_index = tumour_bam + ".bai"

if os.path.exists(tumour_bam) and os.path.exists(tumour_index):
    base_dir = os.path.dirname(tumour_bam)
    unsorted_bam = "%s.bam" % tumour_base
    if os.path.exists(unsorted_bam):
        os.remove(unsorted_bam)
        print("Removed %s" % unsorted_bam) 
    files = os.listdir(base_dir)
    for file in files:
        if file.endswith(".sam") or file.endswith(".fq"):
            remove_file = os.path.join(base_dir,file)
            os.remove(remove_file)
            print("Removed %s" % remove_file)

