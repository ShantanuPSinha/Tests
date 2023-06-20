import os
import re
import json
import csv

def rfixerExtractor (path_to_rfixer_datafile):
    if (not os.path.isfile(path_to_rfixer_datafile)):
        return None

    # This is stupid.
    # data = subprocess.run(['cat', path_to_rfixer_datafile], capture_output=True).stdout.decode('utf-8')

    with open(path_to_rfixer_datafile, 'r') as file:
        data = file.read()

    try:
        pos = re.findall(r'\+\+\+(.*?)---', data, re.DOTALL)
        pos_list = list(filter(None, pos[0].split('\n')))
    except:
        # print (f"Skipping {path_to_rfixer_datafile}")
        return None

    try: 
        neg = re.findall(r'---\n((?:(?!\\n).)*)', data, re.DOTALL)
        neg_list = list(filter(None, neg[0].split('\n')))
    except:
        # print (f"Skipping {path_to_rfixer_datafile}")
        return None

    return pos_list, neg_list


def num_ex_sets(file_in): 
    '''
    This function finds the number of example sets in a csv file containing prompt examples

    Parameters
        file_in: a csv file

    Returns the integer number of example sets in the csv file
    '''

    with open(file_in) as inner:
        in_reader = csv.reader(inner, delimiter=',')

        # get the number of columns in the file
        num_cols = 0 
        for row in in_reader:
            num_cols = len(row)
            break

    return int(num_cols / 2)


def extractCSV (file_in):
    '''
    This function reads in a csv file containing a list of positive and negative examples.

    Parameters
        file_in: a csv file with positive and negative examples in every column

    Returns a list of lists of strings where consecutive columns are corresponding positive and negative examples (index 0 and 1 are a pair of examples, index 2 and 3 are a pair, and so on) 
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

"""

"""
def extractRegel(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    patterns = re.findall(r'"(.*?)",([+\-])', content, re.MULTILINE)

    pos_list = []
    neg_list = []

    for pattern, sign in patterns:
        if sign == '+':
            pos_list.append(pattern)
        elif sign == '-':
            neg_list.append(pattern)

    gt_match = re.search(r'//\s*gt\s*(.*)', content, re.DOTALL)
    gt = gt_match.group(1).strip() if gt_match else ""

    return pos_list, neg_list, gt

def extractAutoTutorTrue (file_path):
    if (not os.path.isfile(file_path)):
        return None

    with open(file_path, 'r') as file:
        data = file.read()

    try:
        pos = re.findall(r'\+\+\+(.*?)---', data, re.DOTALL)
        pos_list = list(filter(None, pos[0].split('\n')))
    except:
        # print (f"Skipping {file_path}")
        return None

    try: 
        neg = re.findall(r'---\n((?:(?!\\n).)*)', data, re.DOTALL)
        neg_list = list(filter(None, neg[0].split('\n')))
    except:
        # print (f"Skipping {file_path}")
        return None

    gt = re.findall(r'(.+)(?=\n\+\+\+)', data)
    return pos_list, neg_list, gt[0]



def convert_dataset_to_json(path_to_dirs, dataset_name, dataset_description, datasetExtractor, outfilename="dataset.json"):
    if isinstance(path_to_dirs, str):
        path_to_dirs = [path_to_dirs]

    dataset = {
        "Dataset Name": dataset_name,
        "Description": dataset_description,
        "Tasks": []
    }


    os.makedirs("Datasets/")

    for path_to_dir in path_to_dirs:
        if not os.path.isdir(path_to_dir):
            #raise SystemExit(f"Directory Path ({path_to_dir}) doesn't exist. Exiting")
            print (f"Directory specified at {path_to_dir} doesn't exist. Continuing")
            continue

        for root, dirs, files in os.walk(path_to_dir):
            for name in files:
                filename = os.path.join(root, name)
                # print("Working on " + name)
                if not (os.path.splitext(filename)[1] == ".txt" or os.path.splitext(filename)[1] == ".csv" or os.path.splitext(filename)[1] == ""):
                   print (f"File: {filename} not a valid type")
                   continue
                
                examples = datasetExtractor(filename)

                if examples == None:
                   continue
                
                if (datasetExtractor == extractCSV):
                  assert isinstance(examples, list)
                  for _ in range (int (len(examples) / 2)):
                    pos_list = examples.pop(0)
                    neg_list = examples.pop(0)

                    dataset["Tasks"].append({
                        "positiveExamples": pos_list,
                        "negativeExamples": neg_list,
                        "groundTruth": []
                    })

                elif (datasetExtractor == extractRegel or datasetExtractor == extractAutoTutorTrue):
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

    with open("Datasets/" + outfilename, "w") as json_file:
        json.dump(dataset, json_file, indent=4)
    
    return dataset

Rfixer = convert_dataset_to_json ("/home/shantanu/duality/RFixer/tests", dataset_name="RFixer", dataset_description="Examples from the RFixer Repository Dataset. The repository dataset was collected from multiple sources including Rebele and AutoTutor", datasetExtractor=rfixerExtractor, outfilename="rfixer_dataset.json")
autoTutor = convert_dataset_to_json ("/home/shantanu/duality/RFixer/tests/clean_AutoTutorWithTrue/", dataset_name="AutoTutor", dataset_description="Examples from Automata Tutor. Data extracted from the RFixer Repository", datasetExtractor=extractAutoTutorTrue, outfilename="automata_tutor.json")
llmCSV = convert_dataset_to_json ("/home/shantanu/duality/llm-regex-prompting/Example Sheets", dataset_name="CSVFiles", dataset_description="CSV Files used for LLM Prompting", datasetExtractor=extractCSV, outfilename="LLMPromptCSV.json")
deepRegex = convert_dataset_to_json ("/home/shantanu/duality/regel/exp/deepregex/benchmark", dataset_name="DeepRegex", dataset_description="Examples from DeepRegex. Data extracted from the Regel Repository", datasetExtractor=extractRegel, outfilename="DeepRegex.json")
stackOverflow = convert_dataset_to_json ("/home/shantanu/duality/regel/exp/so/benchmark", dataset_name="SO", dataset_description="Examples from StackOverflow. Data extracted from the Regel Repository", datasetExtractor=extractRegel, outfilename="StackOverflow.json")

with open("Datasets/dataset.json", "w") as json_file:
    json.dump({ "Datasets": [Rfixer, autoTutor, llmCSV, deepRegex, stackOverflow] }, json_file, indent=4)
