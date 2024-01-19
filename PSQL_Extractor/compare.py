import json
import hashlib, sys, os

def read_ndjson(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def compare_ndjson(file1_path, file2_path, output_file1, output_file2):
    # Function to read NDJSON file
    def read_ndjson(file_path):
        with open(file_path, 'r') as file:
            return [json.loads(line) for line in file]

    # Function to write NDJSON file
    def write_ndjson(data, file_path):
        with open(file_path, 'w') as file:
            for entry in data:
                file.write(json.dumps(entry) + '\n')

    # Read the data from both files
    file1_data = read_ndjson(file1_path)
    file2_data = read_ndjson(file2_path)

    # Extract package_repo URLs and map them back to the original data entries
    file1_urls = {entry['package_repo']: entry for entry in file1_data}
    file2_urls = {entry['package_repo']: entry for entry in file2_data}

    # Find unique URLs
    unique_to_file1_urls = set(file1_urls.keys()) - set(file2_urls.keys())
    unique_to_file2_urls = set(file2_urls.keys()) - set(file1_urls.keys())

    # Get unique data entries
    unique_to_file1 = [file1_urls[url] for url in unique_to_file1_urls]
    unique_to_file2 = [file2_urls[url] for url in unique_to_file2_urls]

    # Write the unique entries to their respective files
    write_ndjson(unique_to_file1, output_file1)
    write_ndjson(unique_to_file2, output_file2)
    print(f"Unique entries written to {output_file1} and {output_file2}")


def modify_file_path(original_path, prefix):
    directory, filename = os.path.split(original_path)
    new_filename = f'{prefix}{filename}'
    return os.path.join(directory, new_filename)


def hash_entry(entry):
    return hashlib.md5(json.dumps(entry, sort_keys=True).encode('utf-8')).hexdigest()

def process_ndjson(file_path, existing_hashes=None):
    unique_entries = []
    unique_hashes = set()
    
    with open(file_path, 'r') as file:
        for line in file:
            entry = json.loads(line)
            entry_hash = hash_entry(entry)
            # If we have a set to compare with and the hash is not in it, add to unique
            if existing_hashes is not None and entry_hash not in existing_hashes:
                unique_entries.append(entry)
            # If there's no set to compare with, we're creating it
            elif existing_hashes is None:
                unique_hashes.add(entry_hash)
    
    return unique_entries if existing_hashes is not None else unique_hashes

def write_ndjson(data, file_path):
    with open(file_path, 'w') as file:
        for entry in data:
            file.write(json.dumps(entry) + '\n')

# Replace these with the absolute paths to your files
file1_path = sys.argv[1] # '/home/shantanu/duality/python-utils/PSQL_Extractor/extracted/npm_packages_100_brokey.ndjson'
file2_path = sys.argv[2] # '/home/shantanu/duality/python-utils/PSQL_Extractor/extracted/npm_packages_100.ndjson'

# Output files
output_file1 = modify_file_path(file1_path, 'unique_to_')
output_file2 = modify_file_path(file2_path, 'unique_to_')

# Run the comparison
compare_ndjson(file1_path, file2_path, output_file1, output_file2)
