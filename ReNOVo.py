#!/usr/bin/env python
# coding=utf-8

# Authors: Emanuele Bonetti (emanuele.bonetti@ieo.it), Giulia Tini (giulia.tini@ieo.it)
# v. 1.0

# ReNOVo is free non-commercial software.
# Users need to obtain the ANNOVAR licence by themselves.
# Contact the Authors for commercial use.

# modules
import subprocess as sp
import sys, os, argparse, tempfile, shutil
from os.path import isfile, join


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


parser = argparse.ArgumentParser(
    description="Given as input a folder containing the VCF or annovar input (AVinput) files, this program applies the Random Forest model of ReNOVo and returns the tabular annovar like files with the classification provided by the model itself."
)
parser.add_argument(
    "-p",
    "--path",
    type=dir_path,
    help="the path to VCFs/AVinputs directory",
    required=True,
)
parser.add_argument(
    "-a",
    "--annovar",
    type=dir_path,
    help="the path to ANNOVAR directory",
    required=True,
)
parser.add_argument(
    "-d",
    "--database",
    type=dir_path,
    default=None,
    help="the path to ANNOVAR database directory, if not defined, annovar/humandb will be used",
)
parser.add_argument(
    "-b",
    "--build",
    type=str,
    default="hg19",
    help="the reference genome build (hg19 or hg38), default is hg19",
)

parser.add_argument(
    "-c",
    "--clinvar",
    type=str,
    default="clinvar_20200316",
    help="Clivar database, default is clinvar_20200316",
)


args = parser.parse_args()

# if not defined, use annovar/humandb
if args.database is None:
    args.database = f"{args.annovar}/humandb"

scripts_folder = f"{os.path.dirname(__file__)}/Scripts/"

# temporary folder creation
if not os.path.exists(args.path + "/temporary"):
    os.mkdir(args.path + "/temporary")

# output dir creation

if not os.path.exists(args.path + "/ReNOVo_output"):
    os.mkdir(args.path + "/ReNOVo_output")

# Get file list
onlyfiles = [f for f in os.listdir(args.path) if isfile(join(args.path, f))]

welcomeMessage = """=============================================================================
ReNOVo 
Interpretation of Pathogenic/Benign for variants using python and R scripts of ReNOVo.
Authors: Emanuele Bonetti (emanuele.bonetti@ieo.it), Giulia Tini (giulia.tini@ieo.it)
v. 1.0

ReNOVo is free non-commercial software. 
Users need to obtain the ANNOVAR licence by themselves. 
Contact the Authors for commercial use.

=============================================================================
"""

endMessage = """=============================================================================
Thanks for using ReNOVo!
=============================================================================
"""

print(welcomeMessage)

# Check annovar dbs
# DBs: refGene,ensGene,avsnp150,gnomad211_exome,dbnsfp35c,intervar_20180118,clinvar_20200316

print("Cheking all ANNOVAR datasets...")

# change this string to upgrade ANNOVAR datasets
dbs = [
    "refGene",
    "ensGene",
    "avsnp150",
    "gnomad211_exome",
    "dbnsfp35c",
    "intervar_20180118",
    args.clinvar,
]

try:
    onlyfiles_annovar = [
        f for f in os.listdir(args.database) if isfile(join(args.database, f))
    ]
    for db in dbs:
        db_str = args.build + "_" + db + ".txt"
        if db_str not in onlyfiles_annovar:
            # download
            command = (
                "perl "
                + args.annovar
                + "/annotate_variation.pl -buildver "
                + args.build
                + " -downdb -webfrom annovar "
                + db
                + " "
                + args.database
            )
            process = sp.Popen(command, shell=True)
            process.wait()
        else:
            print("dataset " + db + " already downloaded... skipping... ")
except IOError:
    print("Error: Annovar path is probably wrong: " + args.annovar)
    sys.exit()

# Run commands for each file
for file_name in onlyfiles:
    command = ""

    # change the commands below to upgrade the ANNOVAR datasets

    if "vcf" in file_name[-3:]:  # check vcf input or AV
        command = (
            "perl "
            + args.annovar
            + "/table_annovar.pl "
            + args.path
            + "/"
            + file_name
            + " "
            + args.database
            + " --buildver "
            + args.build
            + " --out "
            + args.path
            + "/temporary/"
            + file_name
            + " --protocol refGene,ensGene,avsnp150,gnomad211_exome,dbnsfp35c,intervar_20180118,clinvar_20200316 --remove --operation g,g,f,f,f,f,f --nastring . --vcfinput"
        )
        print("VCF file! Launching ANNOVAR!\n")
    elif "avinput" in file_name:
        command = (
            "perl "
            + args.annovar
            + "/table_annovar.pl "
            + args.path
            + "/"
            + file_name
            + " "
            + args.database
            + " --buildver "
            + args.build
            + " --out "
            + args.path
            + "/temporary/"
            + file_name
            + " --protocol refGene,ensGene,avsnp150,gnomad211_exome,dbnsfp35c,intervar_20180118,clinvar_20200316 --remove --operation g,g,f,f,f,f,f --nastring ."
        )
        print("avinput file! Launching ANNOVAR!\n")
    else:
        print(file_name + " is not a VCF or av input... skipped...")
        continue

    # Running Annovar!

    print("ANNOVAR Command: " + command + "\n")
    process = sp.Popen(command, shell=True)
    process.wait()

    # Running preprocessing.R!

    print("Preprocessing... NA imputation and columns names changing... ")
    path_to_an_out = (
        args.path + "/temporary/" + file_name + "." + args.build + "_multianno.txt"
    )
    path_to_temp = args.path + "/temporary/"

    try:
        os.listdir(scripts_folder)
    except OSError:
        print(
            "Error: check scripts folder, if you want to run ReNOVo from any position change the scripts path with the full path"
        )
        sys.exit()

    command = (
        "Rscript "
        + scripts_folder
        + "preprocessing.R "
        + path_to_an_out
        + " "
        + path_to_temp
    )
    process = sp.Popen(command, shell=True)
    process.wait()
    print("DONE!\n")

    # Running Renovo_implementation.py!

    print("ReNOVo implementation... ")
    path_to_Renovo_implementation_input = args.path + "/temporary/input_RF.tab"
    output_file_name = (
        args.path
        + "/ReNOVo_output/"
        + file_name.strip().split(".")[0]
        + "_ReNOVo_and_ANNOVAR_implemented.txt"
    )
    command = (
        "python "
        + scripts_folder
        + "Renovo_implementation.py "
        + path_to_Renovo_implementation_input
        + " "
        + path_to_an_out
        + " "
        + output_file_name
    )
    process = sp.Popen(command, shell=True)
    process.wait()
    print("DONE!\n")

    # output
    print("Output generated! in " + output_file_name + "\n")

# remove temporary directory (and all its content)

dir_to_remove = args.path + "/temporary/"
try:
    shutil.rmtree(dir_to_remove)
except OSError as e:
    print("Error: %s : %s" % (dir_to_remove, e.strerror))

print("removed " + dir_to_remove + "...")

# remove renovo output directory (if empty: program crash o empty input directory)

dir_to_remove = args.path + "/ReNOVo_output/"

if len(os.listdir(dir_to_remove)) == 0:
    try:
        shutil.rmtree(dir_to_remove)
    except OSError as e:
        print("Error: %s : %s" % (dir_to_remove, e.strerror))

    print("removed " + dir_to_remove + "...")


# endMessage
print(endMessage)
