# wfdb-ecg-export
A tutorial on how to convert WFDB databases from physionet to ECG in the pdf format

## Prerequisites
Installed python 3 -> https://www.python.org/downloads/ <br>
Installed pip -> https://pip.pypa.io/en/stable/installation/

## Prepearing the enviroment
In you project folder you need to install the following dependencies:
* Plotting the ecg with matplotlib -> ```pip install matplotlib```
* Reading and formatting the database to an ecg record with wfdb -> ```pip install wfdb```

## Running the script
The script attached will go through a choicen database, for as many records as you have specified and export an pdf to a local destination on your computer. Comments are in the script. The script can by run with the command ```python3 ecgExporter```
<br>
<br>
For further documentation on the WFDB please refer to the [WFDB documentation](https://wfdb.readthedocs.io)
