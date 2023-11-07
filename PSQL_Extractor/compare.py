import json
import hashlib

def read_ndjson(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def compare_ndjson(file1_path, file2_path, output_file1, output_file2):
    # Read the data from both files
    file1_data = read_ndjson(file1_path)
    file2_data = read_ndjson(file2_path)

    # Convert list of dictionaries to list of strings to make comparison faster
    file1_data_str = {json.dumps(entry) for entry in file1_data}
    file2_data_str = {json.dumps(entry) for entry in file2_data}

    # Find unique entries
    unique_to_file1 = file1_data_str - file2_data_str
    unique_to_file2 = file2_data_str - file1_data_str

    # Convert back to dictionaries
    unique_to_file1 = [json.loads(entry) for entry in unique_to_file1]
    unique_to_file2 = [json.loads(entry) for entry in unique_to_file2]

    # Write the unique entries to their respective files
    write_ndjson(unique_to_file1, output_file1)
    write_ndjson(unique_to_file2, output_file2)
    print(f"Unique entries written to {output_file1} and {output_file2}")


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

# def compare_ndjson(file1_path, file2_path, output_file1, output_file2):
#     # Process the first file to get the set of hashes
#     file1_hashes = process_ndjson(file1_path)
#     
#     # Process the second file to find unique entries and get the set of hashes
#     unique_to_file2 = process_ndjson(file2_path, file1_hashes)
#     file2_hashes = process_ndjson(file2_path)
#     
#     # Process the first file again to find unique entries
#     unique_to_file1 = process_ndjson(file1_path, file2_hashes)
#     
#     # Write the unique entries to their respective files
#     write_ndjson(unique_to_file1, output_file1)
#     write_ndjson(unique_to_file2, output_file2)
#     print(f"Unique entries written to {output_file1} and {output_file2}")

# Replace these with the absolute paths to your files
file1_path = '/home/shantanu/duality/python-utils/PSQL_Extractor/extracted/npm_packages_100_brokey.ndjson'
file2_path = '/home/shantanu/duality/python-utils/PSQL_Extractor/extracted/npm_packages_100.ndjson'

# Output files
output_file1 = 'extracted/unique_to_brokey.ndjson'
output_file2 = 'extracted/unique_to_not_brokey.ndjson' # Should be empty

# Run the comparison
compare_ndjson(file1_path, file2_path, output_file1, output_file2)
