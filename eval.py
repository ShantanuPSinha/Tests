import os
import subprocess
import re
from interface import datasetInterface
import shutil

RFixerDir = os.getenv('RFIXER_DIR') or '/home/shantanu/duality/RFixer'

def runRFixer (path_to_testFile):
  return None
  try:
    rfixerProc = subprocess.run(['java', '-jar', '/home/shantanu/duality/RFixer/target/regfixer.jar', '--mode', '1', 'fix', '--file', path_to_testFile], capture_output=True, cwd=RFixerDir, timeout=60)
  except:
    return None

  
  try:
    rfixerProc.check_returncode()
  except:
    print (f"Error Running {path_to_testFile}. Continuing")
    return None
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


if __name__ == "__main__":
  os.makedirs ("rfixer_tests", exist_ok=True)
  i = 0

  interface = datasetInterface('/home/shantanu/duality/eval-RFixer/Datasets/dataset.json')
  for task in interface.task_iterator():
    testfile = f"/home/shantanu/duality/eval-RFixer/rfixer_tests/test{i}"
    # print (f"Running {i}")
    interface.generate_rfixer_testcase (testfile, task)
    rfixerAttempt = runRFixer (testfile)

    if rfixerAttempt == None:
      rfixerAttempt = "RFixer Error"

    task["rfixerAttempt"] = rfixerAttempt
    task["testIndex"] = i
    i = i + 1

    # interface.write_data ("Eval-Rfixer.json")

  interface.write_data ("Eval-Rfixer.json")
  shutil.rmtree("/home/shantanu/duality/eval-RFixer/rfixer_tests/", ignore_errors=True)