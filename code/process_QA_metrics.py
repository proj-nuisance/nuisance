# Processing the JSON files in this folder
import os
import os.path as op
import json
import csv
from glob import glob

# VARIABLES TO BE USED, FILES TO BE OPENED, FILE PATHS TO BE ESTABLISHED
bids_subject = 'qa'
bids_ds_path = op.join('..', 'data', 'QA')

mriqc_path = op.join(bids_ds_path, 'derivatives', 'mriqc', 'derivatives')
ses_path = op.join(bids_ds_path, 'sub-qa', 'ses-*')

# mriqc
first_extraction = open(op.join("..", "data", "extractions", "mriqc_extraction.csv"), "w")
xie = csv.writer(first_extraction)
xie.writerow(["date", "filesuffix", "tsnr", "SAR", "AcquisitionTime", "TxRefAmp"])

# sub-qa
second_extraction = open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w")
other = csv.writer(open(op.join("..", "data", "extractions", "subqa_extraction.csv"), "w"))
other.writerow(["date", "filesuffix", "SAR", "AcquisitionTime", "TxRefAmp"])


# FOR LOOPS TO CREATE INITIAL SPREADSHEET TABLES OF MRIQC DATA

for folder in glob(ses_path):  # os.listdir(os.fsencode("derivatives")):
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

for file in glob(op.join(mriqc_path, f'sub-{bids_subject}*.json')):  # os.listdir(os.fsencode("derivatives")):
    sesame = open(os.fsdecode(file), "r").read()  # open sesameeee
    greetings = json.loads(sesame)
    bids_meta = greetings["bids_meta"]

    if '2017' in os.fsdecode(file):
        if 'tsnr' in greetings and 'SAR' in bids_meta["global"]["const"] and "AcquisitionTime" in bids_meta["time"]["samples"]:
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
second_extraction.close()

# FUNCTION TO ADD QA METRICS


def qa_metric_producer(filename, output_csv):
    start_date = 52
    source = open(op.join("..", "data", "extractions", output_csv), "a")
    product = csv.writer(source)

    for file in glob(op.join(mriqc_path, f'*{filename}*.json')):  # os.listdir(os.fsencode("derivatives")):
        sesame = open(os.fsdecode(file), "r").read()  # open sesameeee
        greetings = json.loads(sesame)
        bids_meta = greetings["bids_meta"]

        if 'SAR' and "AcquisitionTime" and "TxRefAmp" in bids_meta:
            if 'snr_total' in greetings:
                product.writerow([os.fsdecode(file)[start_date:start_date+8],
                                  os.fsdecode(file)[start_date+9:], greetings['snr_total'], bids_meta["SAR"],
                                  bids_meta["AcquisitionTime"], bids_meta["TxRefAmp"]])
            elif 'tsnr' in greetings:
                product.writerow([os.fsdecode(file)[start_date:start_date+8],
                                  os.fsdecode(file)[start_date+9:], greetings['tsnr'], bids_meta["SAR"],
                                  bids_meta["AcquisitionTime"], bids_meta["TxRefAmp"]])

    source.close()

# qa_metric_producer("20180205", "mriqc_extraction.csv")
