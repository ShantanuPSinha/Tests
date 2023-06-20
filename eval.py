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

