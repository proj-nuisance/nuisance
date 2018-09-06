# Processing the JSON files in this folder
import os
import json
import csv

xie = csv.writer(open("extraction.csv", "w")) # named such because that's how you say write in Chinese
xie.writerow(["filename", "SAR", "tsnr"])

for file in os.listdir(os.fsencode("derivatives")):
    sesame = open("derivatives/" + os.fsdecode(file), "r").read() # open sesameeee
    greetings = json.loads(sesame)
    if 'tsnr' in greetings and 'global' in greetings["bids_meta"]: #TODO: key errors pop up that are total chafes
        xie.writerow([os.fsdecode(file), greetings["bids_meta"]["global"]["const"]['SAR'], greetings['tsnr']])