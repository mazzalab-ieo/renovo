# **RENOVO**

## **What it does?**

ReNOVo is a machine learning based software that classifies variants as pathogenic or benign based on publicly available information and provides a Pathogenicity Likelihood Score (PLS).

## **“Files” folder**

  * **median_correct.xlsx**: table with substitutions to perform NA imputation
  * **RF_model.pkl**: trained model of Random Forest
  * **variables.txt**: the set of variables that are used to run the small RF
  * **ordered_cols.txt**: the total set of variables after one-hot-encoding: each level of variable “Type” is considered. Columns are in the correct order to perform new predictions with RF
  * **columns.txt**: file cotaining the columns of interest of the training set, use this file as "-c" argument for rf_trainer.py

## **“Scripts” folder**

  * **preprocessing.R** This file is the first one of the pipeline and performs preprocessing steps such as NA imputation, columns renaming and new variable creation: this is done by calling the function FixData_median.R it takes as input “input_file”, which is the file coming from Annovar annotation and the excel table with medians “median_correct.xlsx”. Its output is the file “input_RF.tab”, which will be the input of the Random Forest.

  * **FixData_median.R**  This is the function which actually performs all the steps above. It takes as input an intermediate dataframe from preprocessing.R and median_correct.xlsx

  * **Renovo_implementation.py**  In this file predictions with RF are performed. The model is already trained, some final preprocessing is done, such as elimination of useless columns and reordering of the useful ones. RF is run and the columns with prediction and with score are saved. It takes as input the files “input_RF.tab” (coming from preprocessing.R), the files with column names “variables.txt” and “ordered_cols.txt”, the file with parameters of the trained model: “RF_model.pkl”.  The output is “output_RF”, that is the input_RF with added the columns with RF prediction and score. NOTE: this output_RF has the NA imputed, **IT IS NOT** the original one.
  
  * **rf_trainer.py** This script create the random forest model using a training set and a file containing the column of interest
## **Usage**

  ReNOVo.py (version 1.0)

  usage: ReNOVo.py [-h] -p, --path PATH -a, --annovar ANNOVAR

  Given as input a folder containing the VCF or annovar input (AVinput) files,
  this program applies the Random Forest model of ReNOVo and returns the tabular
  annovar like files with the classification provided by the model itself.

  optional arguments:
    -h, --help         show this help message and exit
    -p, --path PATH        the path to VCFs/AVinputs directory
    -a, --annovar ANNOVAR  the path to ANNOVAR directory



## **Requirements and Set-up:**

  conda env creation
  ```
  conda env create -f ReNOVo.yml
  ```
  package to install **in the conda env** (commands):
  
  ```
  conda install -c r r-curl r-httr r-rvest r-readxl r-tidyverse
  conda install -c bioconda r-openxlsx
  ```

  python:
  ```
  python -m pip install scikit-learn==0.20.3
  pip install pandas
  pip install matplotlib
  pip install seaborn
  pip install argparse
  ```

  **Troubleshooting:**
  If the R packages are not working properly, try to install them via Rscript as shown below.
  The "tidyverse" package may generate errors with library versions if it does remove the old packages and reinstall them.

  R:
  ```
  Rscript -e "install.packages(c('openxlsx','tidyverse','readxl'), repos='http://cran.us.r-project.org')"
  ```

## **Web Server**

  https://bioserver.ieo.it/shiny/app/renovo

## Data storage

**Training set** https://drive.google.com/file/d/13G6Dn-YzZpS6PK-bhIu_fS1eWR-sQW5T/view?usp=sharing

## License

  ReNOVo is free non-commercial software. Users need to obtain the ANNOVAR licence by themselves. Contact the Authors for commercial use.

## Reference

  ReNOVo is currently under review.
