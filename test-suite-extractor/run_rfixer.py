import subprocess, os, re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

RFIXER_DIR = "/home/shantanu/duality/RFixer"

def extract_solution(output):
    pattern = r"#sol#(.*?)#sol#"
    match = re.search(pattern, output)
    return match.group(1) if match else "NO_SOL"

def execute_java_command(relative_file_path):
    original_directory = os.getcwd()
    os.chdir(RFIXER_DIR)
    
    absolute_file_path = os.path.normpath(os.path.join(original_directory, relative_file_path))
    command = f"java -jar target/regfixer.jar --mode 1 fix --file {absolute_file_path}"
    
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        output = result.stdout.decode()
    except subprocess.TimeoutExpired:
        output = "TIMEOUT"
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        output = None
    finally:
        os.chdir(original_directory)
    return output

def process_file(file, OUTPUT_DIR):
    file_path = os.path.join(OUTPUT_DIR, file)
    output = execute_java_command(file_path)
    file_id = os.path.splitext(file)[0]

    if output == "TIMEOUT":
        return file_id, "TIMEOUT"
    elif output:
        return file_id, extract_solution(output)
    else:
        return file_id, "ERROR"


def run_rfixer(OUTPUT_DIR, max_cores=(os.cpu_count() // 2)):
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    solutions = {}

    with ThreadPoolExecutor(max_workers=max_cores) as executor:
        futures = [executor.submit(process_file, file, OUTPUT_DIR) for file in files]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(files), desc='Processing files', unit='file'):
            file_id, solution = future.result()
            solutions[file_id] = solution

    return solutions
