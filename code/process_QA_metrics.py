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

        # Option("-i", "--input",
        #       dest="input", default="You didn't say where it was coming from",
        #       help="Where do you want the files to be taken from?"),

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
        "Shim1", "Shim2", "Shim3", "Shim4", "Shim5", "Shim6", "Shim7", "Shim8", "snr_total"])

    for item in source:  # os.listdir(os.fsencode("derivatives")):          # for each 
        info = re.search('.*/ses-(?P<date>[0-9]+)/.*', item).groupdict()
       
        # FUNC: abbreviations for easier access to certain dicts in the func/.json files
        func_json = open(os.fsdecode(item), "r").read()  # open sesameeee
        loaded_func = json.loads(func_json)
        func_bids = loaded_func["bids_meta"]
        shim = func_bids["ShimSetting"]

        # ANAT: modifying the func code to access the anatomical JSON
        if int(info["date"]) >= 20171030:
            anat_item = str(item)
            anat_item = anat_item[:34] + "anat" + anat_item[38:]
            anat_item = anat_item[:59] + "acq-MPRAGE_T1w.json"
            
            print(anat_item)
            
            anat_json = open(os.fsdecode(anat_item), "r").read()
            loaded_anat = json.loads(anat_json) 

        print(item); # debugging, indicator that a file's been processed

        # 2018 and later conditions
        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in loaded_func:
            product.writerow([info["date"],
                os.fsdecode(item)[59:], loaded_func["tsnr"], loaded_func["SAR"],
                seconds(loaded_func["AcquisitionTime"]), loaded_func["TxRefAmp"], func_bids["SoftwareVersions"],
                func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7], loaded_anat["snr_total"]])

        # pre 2018 conditions, DOESN'T have TxRefAmp and different location for the other parameters
        else:
            if 'tsnr' in loaded_func and 'SAR' and 'AcquisitionTime' and 'TxRefAmp' in func_bids:
                content = [info["date"], os.fsdecode(item)[59:], loaded_func['tsnr'], func_bids["SAR"],
                    seconds(func_bids["AcquisitionTime"]), func_bids['TxRefAmp'], func_bids["SoftwareVersions"],
                    func_bids["ConversionSoftwareVersion"], func_bids["RepetitionTime"], 
                    shim[0], shim[1], shim[2], shim[3], shim[4], shim[5], shim[6], shim[7]] 
                
                if int(info["date"]) < 20171030:
                    product.writerow(content)
                else:
                    content.append(loaded_anat["snr_total"])
                    product.writerow(content)
            else:
                print("tsnr, SAR or TxRefAmp are not present.")

    destination.close()


def main(args=None):
    parser = get_opt_parser()

    (options, source) = parser.parse_args(args)
    qa_metric_producer(source, options.output_csv)


if __name__ == '__main__':
    main()
