# Programs for Processing Data
This README gives a brief over the function and the use case of each program we developed to analyze our data. The example code was run in bash terminal.

## process_QA_metrics.py
This code processes JSON files containing QA metric information and aggregates them into one CSV file in a pre-designed format that facilitates later analysis.  
```
code/process_QA_metrics.py data/QA/derivatives/mriqc/derivatives/sub-qa_ses-201*
```

## process_real_metrics.py
This code processes JSON files containing real metric information from human patients and aggregates them into one CSV file. Slightly modified from process_QA_metrics.py in that it accounts for different JSON file structure  
```
code/process_real_metrics.py [address of real data]
```

## process_segstats.py
This code processes JSON files containing segmentation statistic information from human patients and aggregates them into on CSV file.
```
code/process_segstats.py [address of segstat info]
```
