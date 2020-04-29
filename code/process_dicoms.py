#!/usr/bin/env python3

# Processing DICOMs
# Chris Cheng 2019

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
import pydicom

# FILE PATHS TO BE ESTABLISHED
bids_subject = 'qa'
bids_ds_path = op.join('data', 'QA')

mriqc_path = op.join(bids_ds_path, 'derivatives', 'mriqc', 'derivatives')
ses_path = op.join(bids_ds_path, 'sub-qa', 'ses-*')


def get_opt_parser():
    # use module docstring for help output
    p = OptionParser()

    p.add_options([
        Option("-o", "--output",
               dest="output_csv",
               #required=True,
               help="Where do you want the extraction to be written to"),

        Option("-t", "--type",
               dest="type", default=None,
               help="Specify what DICOM metadata you want extracted."),

    ])

    return p


def extract_parameter(source, parameters, output_csv):
    
    # opening destination CSV file
    destination = open(output_csv, "a")

    # fires up the CSV writer module
    product = csv.writer(destination)
    
    # WRITES THE HEADER ROW for the CSV
    header = ["Date", "sid", "ses"]
    header.append(parameters)
    product.writerow(header)

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each
        print(item)
        info = re.search('.*?ses-(?P<date>[0-9]+).*', item).groupdict()
        ses = re.search('.*?ses-(?P<ses>[\w]+)_.*', item).groupdict()       # getting session id
        sid = re.search('.*?sid(?P<sid>[0-9]+)_.*', item).groupdict()      # getting subject id

        # merging dicts for easy access
        info.update(ses)
        info.update(sid)

        # FUNC: abbreviations for easier access to certain dicts in the func/.json files
        ds = pydicom.dcmread(item)
        weight = ds.PatientWeight
        
        product.writerow([info["date"], "sub-sid" + info["sid"], info["ses"], weight])
        
    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)

    if options.type == None:
        print("Specify what type of DICOM metadata you want!");
    else:
        extract_parameter(source, options.type, options.output_csv)

if __name__ == '__main__':
    main()
