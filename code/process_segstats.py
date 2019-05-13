#!/usr/bin/env python3

# Processing the JSON files in this folder
# Chris Cheng 2018

import os
import os.path as op
import json
import csv
import re
import datetime
import time

import sys
from optparse import OptionParser, Option
from glob import glob

# FILE PATHS TO BE ESTABLISHED
bids_subject = 'qa'
bids_ds_path = op.join('data', 'QA')

mriqc_path = op.join(bids_ds_path, 'derivatives', 'mriqc', 'derivatives')
ses_path = op.join(bids_ds_path, 'sub-qa', 'ses-*')

fields = ["Background", "Left-Accumbens-area", "Left-Amygdala", "Left-Caudate", "Left-Hippocampus", "Left-Pallidum",
        "Left-Putamen", "Left-Thalamus-Proper", "Right-Accumbens-area", "Right-Amygdala", "Right-Caudate", "Right-Hippocampus", "Right-Pallidum",
        "Right-Putamen", "Right-Thalamus-Proper", "csf", "gray", "white"]


def get_opt_parser():
    # use module docstring for help output
    p = OptionParser()

    p.add_options([
        Option("-o", "--output",
               dest="output_csv",
               #required=True,
               help="Where do you want the extraction to be written to"),

    ])

    return p


def segstats_producer(source, output_csv):
    
    # opening destination CSV file
    destination = open(output_csv, "a")

    # fires up the CSV writer module
    product = csv.writer(destination)
    
    # WRITES THE HEADER ROW for the CSV
    product.writerow(["Date", "sid", "ses", "Background", "Left-Accumbens-area", "Left-Amygdala", "Left-Caudate", "Left-Hippocampus", "Left-Pallidum",
        "Left-Putamen", "Left-Thalamus-Proper", "Right-Accumbens-area", "Right-Amygdala", "Right-Caudate", "Right-Hippocampus", "Right-Pallidum",
        "Right-Putamen", "Right-Thalamus-Proper", "csf", "gray", "white"])

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each
        print(item)
        info = re.search('.*?ses-(?P<date>[0-9]+).*', item).groupdict()     # getting date
        ses = re.search('.*?ses-(?P<ses>[\w]+)_.*', item).groupdict() # getting session id
        sid = re.search('.*?sub-sid(?P<sid>[0-9]+).*', item).groupdict()    # getting subject id
        
        # merging into one dict for easy access
        info.update(ses)
        info.update(sid)
       
        # FUNC: abbreviations for easier access to certain dicts in the func/.json files
        func_json = open(os.fsdecode(item), "r").read()  # open sesameeee
        loaded_func = json.loads(func_json)
       
        print(item); # debugging, indicator that a file's been processed
        
        if "count" in output_csv:
            n = 0
        elif "volume" in output_csv:
            n = 1

        # if all fields are present
        present = True
        for field in fields:
            if field not in loaded_func:
                print("Error: field not found")
                present = False

        if present:
            product.writerow([info["date"], "sub-sid" + info["sid"], info["ses"], 
                loaded_func["Background"][n], loaded_func["Left-Accumbens-area"][n], loaded_func["Left-Amygdala"][n], 
                loaded_func["Left-Caudate"][n], loaded_func["Left-Hippocampus"][n], loaded_func["Left-Pallidum"][n], loaded_func["Left-Putamen"][n],
                loaded_func["Left-Thalamus-Proper"][n], loaded_func["Right-Accumbens-area"][n], loaded_func["Right-Amygdala"][n], 
                loaded_func["Right-Caudate"][n], loaded_func["Right-Hippocampus"][n], loaded_func["Right-Pallidum"][n], loaded_func["Right-Putamen"][n], 
                loaded_func["Right-Thalamus-Proper"][n], loaded_func["csf"][n], loaded_func["gray"][n], loaded_func["white"][n]])

        else:
                print("One of the fields is not present.")

    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)

    ses_csv = options.output_csv[:-4] + "-count" + options.output_csv[-4:]
    sid_csv = options.output_csv[:-4] + "-volume" + options.output_csv[-4:]
    segstats_producer(source, ses_csv)
    segstats_producer(source, sid_csv)


if __name__ == '__main__':
    main()
