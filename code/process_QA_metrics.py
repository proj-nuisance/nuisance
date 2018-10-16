#!/usr/bin/env python3

# Processing the JSON files in this folder
# Chris Cheng 2018

import os
import os.path as op
import json
import csv
import re

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


def extract_sub_qa(files):

    second_extraction = open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w")
    other = csv.writer(open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w"))
    other.writerow(["date", "filesuffix", "SAR", "AcquisitionTime", "TxRefAmp"])

    for folder in files:  # os.listdir(os.fsencode("derivatives")):
        for file in glob(op.join(folder, 'func', 'sub-{bids_subject}*.json')):
            sesame = open(os.fsdecode(file), "r").read()  # open sesameeee
            greetings = json.loads(sesame)

            if '2018' in os.fsdecode(file):
                if 'SAR' and "AcquisitionTime" and "TxRefAmp" in greetings:
                    other.writerow([os.fsdecode(file)[47:55], os.fsdecode(file)[56:], greetings["SAR"],
                                    greetings["AcquisitionTime"], greetings["TxRefAmp"]])

            else:
                if 'SAR' in greetings["global"]["const"] and "AcquisitionTime" in greetings["time"]["samples"]:
                    other.writerow([os.fsdecode(file)[47:55], os.fsdecode(file)[56:],
                                  greetings["global"]["const"]["SAR"], greetings["time"]["samples"]["AcquisitionTime"]])
    second_extraction.close()


def extract_mriqc():

    first_extraction = open(op.join("..", "data", "extractions", "mriqc_extraction.csv"), "w")
    xie = csv.writer(first_extraction)
    xie.writerow(["date", "filesuffix", "tsnr", "SAR", "AcquisitionTime", "TxRefAmp"])

    for file in glob(op.join(mriqc_path, 'sub-{bids_subject}*.json')):  # os.listdir(os.fsencode("derivatives")):
        sesame = open(os.fsdecode(file), "r").read()  # open sesameeee
        greetings = json.loads(sesame)
        bids_meta = greetings["bids_meta"]

        if '2017' in os.fsdecode(file):
            if 'tsnr' in greetings and 'SAR' in bids_meta["global"]["const"] \
                    and "AcquisitionTime" in bids_meta["time"]["samples"]:
                xie.writerow([os.fsdecode(file)[52:60], os.fsdecode(file)[61:], greetings['tsnr'],
                              bids_meta["global"]["const"]["SAR"], bids_meta["time"]["samples"]["AcquisitionTime"]])

        elif '2018' in os.fsdecode(file):
            if 'SAR' and "AcquisitionTime" and "TxRefAmp" in bids_meta:
                if 'snr_total' in greetings:
                    xie.writerow([os.fsdecode(file)[52:60], os.fsdecode(file)[61:], greetings['snr_total'],
                                  bids_meta["SAR"], bids_meta["AcquisitionTime"], bids_meta["TxRefAmp"]])
                elif 'tsnr' in greetings:
                    xie.writerow([os.fsdecode(file)[52:60], os.fsdecode(file)[61:], greetings['tsnr'],
                              bids_meta["SAR"], bids_meta["AcquisitionTime"],
                                 bids_meta["TxRefAmp"]])

    first_extraction.close()


def qa_metric_producer(source, output_csv):
    
    destination = open(output_csv, "a")
    product = csv.writer(destination)

    for item in source:  # os.listdir(os.fsencode("derivatives")):
        info = re.search('.*/ses-(?P<date>[0-9]+)/.*', item).groupdict()
        sesame = open(os.fsdecode(item), "r").read()  # open sesameeee
        greetings = json.loads(sesame)
        print(item)  # debugging
        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in greetings:
            product.writerow([info["date"],
                os.fsdecode(item)[49:], greetings["tsnr"], greetings["SAR"],
                greetings["AcquisitionTime"], greetings["TxRefAmp"]])

        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            bids_meta = greetings["bids_meta"]
            if 'tsnr' in greetings and 'SAR' and 'AcquisitionTime' and 'TxRefAmp' in bids_meta:
                product.writerow([info["date"], os.fsdecode(item)[49:],
                                  greetings['tsnr'], bids_meta["SAR"],
                                  bids_meta["AcquisitionTime"], bids_meta['TxRefAmp']])
            else:
                product.writerow("something went wrong")

    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)
    qa_metric_producer(source, options.output_csv)


if __name__ == '__main__':
    main()
