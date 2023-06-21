"""
Script for extracting Positive and Negative examples from various datasets
and converting them to JSON files.
"""
# Shantanu Sinha

import os
import re
import json
import csv

# Output to same directory or in the parent directory (is parent higher?)
outputToSameDir = False
outdir = "Datasets/" if outputToSameDir else os.path.join(os.pardir, "json_datasets/") # Alternatively, just define an absolute path that's convienient

try:
    os.makedirs(outdir, exist_ok=True)
except FileExistsError:
    pass


def rfixerExtractor(path_to_rfixer_datafile, diag=False):
    """
    Extracts positive and negative lists from an RFixer data file.

    Args:
        path_to_rfixer_datafile (str): The path to the RFixer data file.
        diag (bool, optional): Flag to enable diagnostic printing. Defaults to False.

    Returns:
        tuple: A tuple containing the positive list and negative list extracted from the data file.
               If extraction fails or the file does not exist, returns None.
    """

    if not os.path.isfile(path_to_rfixer_datafile):
        return None
    
    # This is stupid.
    # data = subprocess.run(['cat', path_to_rfixer_datafile], capture_output=True).stdout.decode('utf-8')

    # Read the contents of the data file
    with open(path_to_rfixer_datafile, 'r') as file:
        data = file.read()

    try:
        # Extract the text between '+++' and '---' using regex
        pos = re.findall(r'\+\+\+(.*?)---', data, re.DOTALL)
        pos_list = list(filter(None, pos[0].split('\n')))
    except:
        # Extraction failed
        if diag:
            print(f"Skipping {path_to_rfixer_datafile}")
        return None

    try:
        # Extract the text after '---' using regex
        neg = re.findall(r'---\n((?:(?!\\n).)*)', data, re.DOTALL)
        neg_list = list(filter(None, neg[0].split('\n')))
    except:
        # Extraction failed
        if diag:
            print(f"Skipping {path_to_rfixer_datafile}")
        return None

    return pos_list, neg_list



def num_ex_sets(file_in):
    '''
    This function finds the number of example sets in a csv file containing prompt examples

    Parameters
        file_in: a csv file

    Returns the integer number of example sets in the csv file

    Author: Sophie Chen
    '''

    with open(file_in) as inner:
        in_reader = csv.reader(inner, delimiter=',')

        # get the number of columns in the file
        num_cols = 0
        for row in in_reader:
            num_cols = len(row)
            break

    return int(num_cols / 2)


def extractCSV(file_in):
    '''
    This function reads in a csv file containing a list of positive and negative examples.

    Parameters
        file_in: a csv file with positive and negative examples in every column

    Returns a list of lists of strings where consecutive columns are corresponding positive and negative examples (index 0 and 1 are a pair of examples, index 2 and 3 are a pair, and so on) 
    Author: Sophie Chen
    '''
    examples = []

    with open(file_in) as inner:
        in_reader = csv.reader(inner, delimiter=',')

        # add placeholders for each column to examples
        for i in range(num_ex_sets(file_in) * 2):
            examples.append([])

        # add examples to examples
        # first line is column names
        line = 0
        for row in in_reader:
            if line == 0:
                line += 1
            else:
                for column in range(len(row)):
                    examples[column].append(row[column])

    return examples


def extractRegel(file_path):
    """
    Extracts examples from files in the format of Regel Inputs.

    Args:
        file_path (str): The path to the Regel file.

    Returns:
        tuple: A tuple containing the positive list, negative list, and ground truth extracted from the file.
    """

    with open(file_path, 'r') as file:
        content = file.read()

    # Find all patterns enclosed in double quotes followed by a comma and a sign (+/-)
    patterns = re.findall(r'"(.*?)",([+\-])', content, re.MULTILINE)

    pos_list = []
    neg_list = []

    for pattern, sign in patterns:
        if sign == '+':
            pos_list.append(pattern)
        elif sign == '-':
            neg_list.append(pattern)

    # Find the ground truth text after the "// gt" comment
    gt_match = re.search(r'//\s*gt\s*(.*)', content, re.DOTALL)
    gt = gt_match.group(1).strip() if gt_match else ""

    return pos_list, neg_list, gt



def extractAutoTutorTrue(file_path):
    """
    Extracts examples from files in the AutoTutor format. 
    True indicates that the file had the ground truth regex included

    Args:
        file_path (str): The path to the AutoTutor True file.

    Returns:
        tuple: A tuple containing the positive list, negative list, and ground truth extracted from the file.
               If extraction fails or the file does not exist, returns None.
    """

    if not os.path.isfile(file_path):
        return None

    with open(file_path, 'r') as file:
        data = file.read()

    try:
        # Extract the text between '+++' and '---' using regex
        pos = re.findall(r'\+\+\+(.*?)---', data, re.DOTALL)
        pos_list = list(filter(None, pos[0].split('\n')))
    except:
        return None

    try:
        # Extract the text after '---' using regex
        neg = re.findall(r'---\n((?:(?!\\n).)*)', data, re.DOTALL)
        neg_list = list(filter(None, neg[0].split('\n')))
    except:
        return None

    # Extract the ground truth before '+++' occurs
    gt = re.findall(r'(.+)(?=\n\+\+\+)', data)

    return pos_list, neg_list, gt[0]


def golfExtractor(path_to_golf_dir):
    """
    Extracts examples from files in the golf format.

    Args:
        path_to_golf_dir (str): The path to the golf directory.

    Returns:
        tuple: A tuple containing the positive list and negative list extracted from the files.
               If the directory doesn't exist or the files are not found, returns None.
    """

    if not os.path.isdir(path_to_golf_dir):
        print(f"Directory specified at {path_to_golf_dir} doesn't exist. Continuing")
        return None

    # This silliness is required because the structure that the Genetic Golf Solver Expects
    with open(path_to_golf_dir + "/left.txt", "r") as f:
        pos_list = f.read().split("\n")

    with open(path_to_golf_dir + "/right.txt", "r") as f:
        neg_list = f.read().split("\n")

    return pos_list, neg_list


def convert_dataset_to_json(path_to_dirs, dataset_name, dataset_description, datasetExtractor, outfilename="dataset.json", outputToSameDir=False):
    """
    Converts a dataset extracted from multiple directories/files into a JSON file.

    Args:
        path_to_dirs (str or list): The path(s) to the directories/files containing the dataset.
        dataset_name (str): The name of the dataset.
        dataset_description (str): The description of the dataset.
        datasetExtractor (function): The function to extract examples from the dataset.
        outfilename (str, optional): The name of the output JSON file. Defaults to "dataset.json".

    Returns:
        dict: The dataset dictionary.
    """

    if isinstance(path_to_dirs, str):
        path_to_dirs = [path_to_dirs]

    dataset = {
        "Dataset Name": dataset_name,
        "Description": dataset_description,
        "Tasks": []
    }

    for path_to_dir in path_to_dirs:
        if not os.path.isdir(path_to_dir):
            print(f"Directory specified at {path_to_dir} doesn't exist. Continuing")
            continue

        for root, dirs, files in os.walk(path_to_dir):
            if datasetExtractor == golfExtractor:
                for dir in dirs:
                    pos_list, neg_list = datasetExtractor(os.path.join(root, dir))
                    dataset["Tasks"].append({
                        "positiveExamples": pos_list,
                        "negativeExamples": neg_list,
                        "groundTruth": ""
                    })
                break

            for name in files:
                filename = os.path.join(root, name)
                if not (os.path.splitext(filename)[1] == ".txt" or os.path.splitext(filename)[1] == ".csv" or os.path.splitext(filename)[1] == ""):
                    print(f"File: {filename} not a valid type")
                    continue

                examples = datasetExtractor(filename)

                if examples is None:
                    continue

                elif datasetExtractor == extractCSV:
                    assert isinstance(examples, list)
                    while examples:
                        pos_list = examples.pop(0)
                        neg_list = examples.pop(0)
                        dataset["Tasks"].append({
                            "positiveExamples": pos_list,
                            "negativeExamples": neg_list,
                            "groundTruth": []
                        })

                elif datasetExtractor in (extractRegel, extractAutoTutorTrue):
                    pos_list, neg_list, gt = examples
                    dataset["Tasks"].append({
                        "positiveExamples": pos_list,
                        "negativeExamples": neg_list,
                        "groundTruth": gt
                    })

                else:
                    pos_list, neg_list = examples
                    dataset["Tasks"].append({
                        "positiveExamples": pos_list,
                        "negativeExamples": neg_list,
                        "groundTruth": []
                    })

    with open(outdir + outfilename, "w") as json_file:
        json.dump(dataset, json_file, indent=4)

    return dataset



datasets = [
    {
        "path": "/home/shantanu/duality/RFixer/tests",
        "name": "RFixer",
        "description": "Examples from the RFixer Repository Dataset. The repository dataset was collected from multiple sources including Rebele and AutoTutor",
        "extractor": rfixerExtractor,
        "filename": "rfixer_dataset.json"
    },
    {
        "path": "/home/shantanu/duality/RFixer/tests/clean_AutoTutorWithTrue/",
        "name": "AutoTutor",
        "description": "Examples from Automata Tutor. Data extracted from the RFixer Repository",
        "extractor": extractAutoTutorTrue,
        "filename": "automata_tutor.json"
    },
    {
        "path": "/home/shantanu/duality/llm-regex-prompting/Example Sheets",
        "name": "CSVFiles",
        "description": "CSV Files used for LLM Prompting",
        "extractor": extractCSV,
        "filename": "LLMPromptCSV.json"
    },
    {
        "path": "/home/shantanu/duality/regel/exp/deepregex/benchmark",
        "name": "DeepRegex",
        "description": "Examples from DeepRegex. Data extracted from the Regel Repository",
        "extractor": extractRegel,
        "filename": "DeepRegex.json"
    },
    {
        "path": "/home/shantanu/duality/regel/exp/so/benchmark",
        "name": "SO",
        "description": "Examples from StackOverflow. Data extracted from the Regel Repository",
        "extractor": extractRegel,
        "filename": "StackOverflow.json"
    },
    {
        "path": ["/home/shantanu/duality/regex-golf/instances/", "/home/shantanu/duality/regex-golf/instances.ours/"],
        "name": "Golf",
        "description": "Examples from Golf",
        "extractor": golfExtractor,
        "filename": "golf.json"
    }
]


master_dataset = {"Datasets": [convert_dataset_to_json(dataset["path"], dataset["name"], dataset["description"], dataset["extractor"], outfilename=dataset["filename"], outputToSameDir=outputToSameDir) for dataset in datasets]}
with open(outdir + "dataset.json", "w") as json_file:
    json.dump(master_dataset, json_file, indent=4)