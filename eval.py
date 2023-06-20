import os
import subprocess
import re
import json
import csv

RFixerDir = os.getenv('RFIXER_DIR') or '/home/shantanu/duality/RFixer'

def runRFixer (path_to_testFile):
  rfixerProc = subprocess.run(['java', '-jar', '/home/shantanu/duality/RFixer/target/regfixer.jar', '--mode', '1', 'fix', '--file', path_to_testFile], capture_output=True, cwd=RFixerDir)
  rfixerProc.check_returncode()
  testOutput = rfixerProc.stdout.decode('utf-8')

  # print (testOutput)
  match_re = re.compile (r'(?<=#sol#).*(?=#sol#)')
  regex = match_re.search(testOutput).group(0)
  return regex


def runGeneticSolver (path_to_testFile):
   return "Genetic Solver not integrated"

"""
Positive_examples: List of strings which are Positive Examples (i.e should be matched by the input Regex)
Positive_examples: List of strings which are Negative Examples (i.e should not be matched by the input Regex)
Regex: Regular expression under test.

Function calculates accuracy of a generated regex, but comparing each regex to the input examples that were used
to generate it. Returns an integer that is meant to be interpreted as a percentage value of correct "tests" passed.

"""
def calc_accuracy (positive_examples, negative_examples, regex):
  score = 0

  print (regex)
  dut_regex = re.compile (regex)

  for input_string in positive_examples:
    if dut_regex.match (input_string):
      print ("Matched Positive String " + input_string)
      score += 1
    else:
      print ("Did not match Positive String " + input_string)

  for input_string in negative_examples:
    if dut_regex.match (input_string):
      print ("Matched Negative String " + input_string)
    else:
      print ("Did not match Negative String " + input_string)
      score += 1

  total = len(positive_examples) + len(negative_examples)
  return score / total


def rfixerExtractor (path_to_rfixer_datafile):
    if (not os.path.isfile(path_to_rfixer_datafile)):
        return None

    data = subprocess.run(['cat', path_to_rfixer_datafile], capture_output=True).stdout.decode('utf-8')

    try:
        pos = re.findall(r'\+\+\+(.*?)---', data, re.DOTALL)
        pos_list = list(filter(None, pos[0].split('\n')))
    except:
        print (f"Skipping {path_to_rfixer_datafile}")
        return None

    try: 
        neg = re.findall(r'---\n((?:(?!\\n).)*)', data, re.DOTALL)
        neg_list = list(filter(None, neg[0].split('\n')))
    except:
        print (f"Skipping {path_to_rfixer_datafile}")
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
   


def convert_dataset_to_json(path_to_dirs, dataset_name, dataset_description, datasetExtractor, outfilename="dataset.json"):
    if isinstance(path_to_dirs, str):
        path_to_dirs = [path_to_dirs]

    dataset = {
        "Dataset Name": dataset_name,
        "Description": dataset_description,
        "Tasks": []
    }

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
            
                else:
                    pos_list, neg_list = examples
                    dataset["Tasks"].append({
                        "positiveExamples": pos_list,
                        "negativeExamples": neg_list,
                        "groundTruth": []
                    })

    with open(outfilename, "w") as json_file:
        json.dump(dataset, json_file, indent=4)


RFixer_Datasets = ["/home/shantanu/duality/RFixer/tests/allRebele", "/home/shantanu/duality/RFixer/tests/benchmark_corpus", "/home/shantanu/duality/RFixer/tests/clean_AutoTutor", "/home/shantanu/duality/RFixer/tests/benchmark_explicit", "/home/shantanu/duality/RFixer/tests/benchmark_explicit2"]

convert_dataset_to_json (RFixer_Datasets, dataset_name="RFixer Dataset", dataset_description="Examples from the RFixer Repository Dataset", datasetExtractor=rfixerExtractor, outfilename="rfixer_dataset.json")