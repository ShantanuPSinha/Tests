import subprocess, os, re, json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

RFIXER_DIR = "/home/shantanu/duality/RFixer/"

def extract_solution(output):
    pattern = r"#sol#(.*?)#sol#"
    match = re.search(pattern, output)
    return match.group(1) if match else "NO_SOL"

def generate_RFixer_input(filtered_data, directory, OR_INPUTS=False):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if re.match(r'^\d+\.txt$', filename):
                os.remove(os.path.join(directory, filename))
    else:
        os.makedirs(directory)

    for entry in filtered_data:
        file_name = f"{directory}/{entry['id']}.txt"
        with open(file_name, 'w') as file:
            if OR_INPUTS:
                file.write(f"{entry['positive_inputs'][0]}|{entry['negative_inputs'][0]}" + '\n')
            else:
                file.write("w*" + '\n')
            file.write('+++\n')
            file.write('\n'.join(entry['positive_inputs']) + '\n')
            file.write('---\n')
            file.write('\n'.join(entry['negative_inputs']) + '\n')


def execute_java_command(relative_file_path: str, TIMEOUT=10):
    absolute_file_path = os.path.normpath(os.path.join(os.getcwd(), relative_file_path))
    jar_path = os.path.join(RFIXER_DIR, 'target/regfixer.jar')
    command = ["java", "-jar", jar_path, "--mode", "1", "fix", "--file", absolute_file_path]

    try:
        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=RFIXER_DIR)

        try:
            # Wait for the command to complete, with timeout
            stdout, stderr = process.communicate(timeout=TIMEOUT)
            output = stdout.decode()
        except subprocess.TimeoutExpired:
            process.kill()
            # Skipping the file after timeout
            output = "TIMEOUT"
        except Exception as e:
            output = None

    except subprocess.CalledProcessError as e:
        output = None

    return output

def process_file(file, OUTPUT_DIR, timeout=10) -> (int, str):
    file_path = os.path.join(OUTPUT_DIR, file)
    output = execute_java_command(file_path, timeout)
    file_id = int (os.path.splitext(file)[0])
    print (f"Processed: {file_id}")

    if output == "TIMEOUT":
        return file_id, "TIMEOUT"
    elif output:
        return file_id, extract_solution(output)
    else:
        return file_id, "ERROR"

def run_rfixer(OUTPUT_DIR, use_multithreading=True, max_cores=(os.cpu_count() + 4), timeout=10):
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    ndjson_file_path = os.path.join(OUTPUT_DIR, '.temp_sols.ndjson')

    solutions = {}

    def append_solution_to_ndjson_and_collect(file_id, solution):
        # Append solution to NDJSON file
        with open(ndjson_file_path, 'a') as ndjson_file:
            record = json.dumps({'file_id': file_id, 'solution': solution})
            ndjson_file.write(record + '\n')
        # Collect solution in memory
        solutions[file_id] = solution


    def process_files_sequentially():
        for file in tqdm(files, desc='Processing files', unit='file'):
            file_id, solution = process_file(file, OUTPUT_DIR, timeout)
            append_solution_to_ndjson_and_collect(file_id, solution)


    def process_files_multithreaded():
        with ThreadPoolExecutor(max_cores) as executor:
            futures = [executor.submit(process_file, file, OUTPUT_DIR, timeout) for file in files]
            for future in concurrent.futures.as_completed(futures):
                file_id, solution = future.result()
                append_solution_to_ndjson_and_collect(file_id, solution)

    if use_multithreading:
        process_files_multithreaded()
    else:
        process_files_sequentially()

    return solutions
