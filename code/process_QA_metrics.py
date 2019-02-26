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


def get_opt_parser():
    # use module docstring for help output
    p = OptionParser()

    p.add_options([
        Option("-o", "--output",
               dest="output_csv",
               #required=True,
               help="Where do you want the extraction to be written to"),

        Option("-i", "--input",
               dest="input", default="You didn't say where it was coming from",
               help="Where do you want the files to be taken from?"),

    ])

    return p


def seconds(input):
    x = time.strptime(input.split('.')[0],'%H:%M:%S')
    return int(datetime.timedelta(hours = x.tm_hour, minutes = x.tm_min, seconds = x.tm_sec).total_seconds())


def qa_metric_producer(source, output_csv):
    
    # opening destination CSV file
    destination = open(output_csv, "a")

    # fires up the CSV writer module
    product = csv.writer(destination)
    
    # WRITES THE HEADER ROW for the CSV
    product.writerow(["Date", "Filetype", "tsnr", "SAR", "AcquisitionTime", "TxRefAmp", "SoftwareVersions", "CSV", "RepetitionTime", 
        "Shim1", "Shim2", "Shim3", "Shim4", "Shim5", "Shim6", "Shim7", "Shim8"])

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each 
        info = re.search('.*/ses-(?P<date>[0-9]+)/.*', item).groupdict()
        sesame = open(os.fsdecode(item), "r").read()  # open sesameeee
        greetings = json.loads(sesame)
        bids_meta = greetings["bids_meta"]
        shim = bids_meta["ShimSetting"]

        print(item); # debugging

        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in greetings:
            product.writerow([info["date"],
                os.fsdecode(item)[59:], greetings["tsnr"], greetings["SAR"],
                seconds(greetings["AcquisitionTime"]), greetings["TxRefAmp"], bids_meta["SoftwareVersions"],
                bids_meta["ConversionSoftwareVersion"], bids_meta["RepetitionTime"], 
                shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7]])

        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            if 'tsnr' in greetings and 'SAR' and 'AcquisitionTime' and 'TxRefAmp' in bids_meta:
                product.writerow([info["date"], os.fsdecode(item)[59:],
                                  greetings['tsnr'], bids_meta["SAR"],
                                  seconds(bids_meta["AcquisitionTime"]), bids_meta['TxRefAmp'], bids_meta["SoftwareVersions"],
                                  bids_meta["ConversionSoftwareVersion"], bids_meta["RepetitionTime"], 
                                  shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7]])
            else:
                product.writerow("something went wrong")

    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)
    qa_metric_producer(source, options.output_csv)


if __name__ == '__main__':
    main()
