#!/usr/bin/env python

# Processing the JSON files in this folder
# Chris Cheng 2018

import os
import os.path as op
import json
import csv

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
               dest="output_csv", default='You didnt say where to write it to',
               help="Where do you want the extraction to be written to"),
    ])

    return p


def extract_sub_qa(files):

    second_extraction = open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w")
    other = csv.writer(open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w"))
    other.writerow(["date", "filesuffix", "SAR", "AcquisitionTime", "TxRefAmp"])

    for folder in files:  # os.listdir(os.fsencode("derivatives")):
        for file in glob(op.join(folder, 'func', f'sub-{bids_subject}*.json')):
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

    for file in glob(op.join(mriqc_path, f'sub-{bids_subject}*.json')):  # os.listdir(os.fsencode("derivatives")):
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


def qa_metric_producer(sources, output_csv):

    start_date = 49  # index for date that the QA metrics were taken in the file name
    destination = open(output_csv, "a")
    product = csv.writer(destination)

    for file in sources:
        opened_file = open(os.fsdecode(file), "r").read()
        overall_metrics = json.loads(opened_file)
        bids_meta = overall_metrics["bids_meta"]

        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in bids_meta:
            if 'snr_total' in overall_metrics:
                product.writerow([os.fsdecode(file)[start_date:start_date+8],
                                  os.fsdecode(file)[start_date+9:], overall_metrics['snr_total'], bids_meta["SAR"],
                                  bids_meta["AcquisitionTime"], bids_meta["TxRefAmp"]])
            elif 'tsnr' in overall_metrics:
                product.writerow([os.fsdecode(file)[start_date:start_date+8],
                                  os.fsdecode(file)[start_date+9:], overall_metrics['tsnr'], bids_meta["SAR"],
                                  bids_meta["AcquisitionTime"], bids_meta["TxRefAmp"]])

        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            if 'tsnr' in overall_metrics and 'SAR' in bids_meta["global"]["const"] \
                    and "AcquisitionTime" in bids_meta["time"]["samples"]:
                product.writerow([os.fsdecode(file)[start_date:start_date+8], os.fsdecode(file)[start_date+9:],
                                  overall_metrics['tsnr'], bids_meta["global"]["const"]["SAR"],
                                  bids_meta["time"]["samples"]["AcquisitionTime"]])

    destination.close()


def main(args=None):
    parser = get_opt_parser()
    (options, sources) = parser.parse_args(args)

    qa_metric_producer(sources, options.output_csv)


if __name__ == '__main__':
    main()
