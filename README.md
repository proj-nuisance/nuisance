# MRI Nuisance

## Introduction
This repository contains preprocessing and analysis scripts for a paper pending publication, "A new virtue of phantom MRI data: explaining variance in human participant data." by Chris Cheng and Yaroslav Halchenko.

This dataset is available through [DataLad](http://datasets.datalad.org/?dir=/dbic).

## Setting up the environment

We recommend using either a [NeuroDebian](http://neuro.debian.net/)
virtual machine, or a container (Docker or Singularity) with NeuroDebian
installed to replicate these analyses. In particular, the Python scripts
might rely on specific versions of python packages. If you're using conda, you can get started as follows:

```
conda create --name famface python=2.7
pip install -r requirements.txt
```

You should also have FSL and ANTs installed.

## Repository Structure

### `code/`

This README gives a brief over the function and the use case of each program we developed to analyze our data. The example code was run in bash terminal.

- [`process_QA_metrics.py`](code/process_QA_metrics.py):
This code processes JSON files containing QA metric information and aggregates them into one CSV file in a pre-designed format that facilitates later analysis.  
```
code/process_QA_metrics.py data/QA/derivatives/mriqc/derivatives/sub-qa_ses-201*
```

- [`process_real_metrics.py`](code/process_real_metrics.py):
This code processes JSON files containing real metric information from human patients and aggregates them into one CSV file. Slightly modified from process_QA_metrics.py in that it accounts for different JSON file structure  
```
code/process_real_metrics.py [address of real data]
```

- [`process_segstats.py`](code/process_segstats.py):
This code processes JSON files containing segmentation statistic information from human patients and aggregates them into on CSV file.
```
code/process_segstats.py [address of segstat info]
```

### `data/`
- [`QA`](data/QA):
This folder contains the QA data for DBIC MRI data.

- [`extractions`](data/extractions):
This folder contains CSV files with preprocessing scripts outputting the extracted data from QA and DBIC.

- [`QA-mriqc`](data/QA-mriqc):
This folder contains fMRI QA data.

- [`dbic`](data/dbic):
This folder contains real human data from the DBIC and a folder, [`scripts`](data/dbic/scripts), that processes that data by converting data to a BIDS format using heudiconv and extracting certain additional features such as patient weight and the date the data was recorded.

### `ipy/`
- [`nuisance_QA_data.ipynb`](ipy/nuisance_QA_data.ipynb):
This Jupyter Notebook file carries out exploratory data analyses on extracted QA data.

- [`nuisance_real_data.ipynb`](ipy/nuisance_real_data.ipynb):
This Jupyter Notebook file carries out data analyses on extracted QA data and real data.

- [`nuisancelib.py`](ipy/nuisancelib.py):
This Python script contains all the files for building models, including orthogonalization, creating regression models, conducting F-tests, etc.
