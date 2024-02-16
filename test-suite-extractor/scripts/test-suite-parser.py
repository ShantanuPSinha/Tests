#! /usr/bin/python3
import json
import argparse
import sys
import os

def is_file_empty(file_path):
    """Check if a file is empty by reading its size."""
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return os.path.getsize(file_path) == 0
    else:
        return True 

def cleanUp(json_obj: dict) -> dict:
    """
    Clean the provided JSON object by removing specific entries and duplicates.

    This function inspects the JSON object to remove any entries that have "node_modules" 
    or "internal/modules" within the file path and eliminates any duplicate 'usage' entries.

    Arguments:
    json_obj (dict): The JSON object that needs cleaning. 

    Returns:
    dict: The cleaned JSON object with unwanted file path entries and duplicates removed. 
          The structure of the object remains the same; only the content is filtered.
    """

    if 'usages' not in json_obj:
        return json_obj

    cleaned_usages = {}

    for inputs, usage_list in json_obj.get('usages', {}).items():
        cleaned_list = []
        seen_entries = set()  # keep track of unique entries

        for usage in usage_list:
            if 'entries' in usage:
                new_entries = []

                for entry in usage.get('entries', []):
                    entry_json = json.dumps(entry, sort_keys=True)
                    
                    if entry_json in seen_entries:
                        continue

                    file_info = entry.get('file_info')
                    if file_info:
                        file_path = file_info.get('file_path', '')
                        caller_info = entry.get('caller', {})

                        # filter out the unwanted paths.
                        if ('node_modules' not in file_path and 
                            "internal/modules" not in file_path and 
                            caller_info.get('object') == "RegExp"):
                            new_entries.append(entry)
                            seen_entries.add(entry_json)  # Mark this entry as seen

                if new_entries:
                    usage['entries'] = new_entries
                    cleaned_list.append(usage)

        if cleaned_list:
            cleaned_usages[inputs] = cleaned_list

    json_obj['usages'] = cleaned_usages

    return json_obj


def transform_json(original_json: dict) -> list:
    """
    Transform the provided JSON object into a list of new JSON structure.

    Arguments:
    original_json (dict): The original JSON object containing detailed project and usage data.

    Returns:
    list: A list of dictionaries, each containing selected information from the original JSON.
    """

    base_data = {
        "regex": original_json.get("pattern"),
        "inputs": list(original_json.get("usages", {}).keys()),
        "project_repo_url": original_json.get("project_repo_url"),
    }

    file_paths = set()
    for usage_list in original_json.get("usages", {}).values():
        for usage in usage_list:
            for entry in usage.get("entries", []):
                file_info = entry.get("file_info")
                if file_info:
                    file_path = file_info.get("file_path")
                    if file_path:
                        file_paths.add(file_path)

    # Create a result_data object for each unique file path. Not sure if we need this
    result = []
    for file_path in file_paths:
        data = base_data.copy()
        data["file_path"] = file_path
        result.append(data)

    return result

def ndjson_printer(input_file_path : str, output_file_path : str) -> None:
    """
    Reads an NDJSON file, pretty-prints the JSON objects, and writes them to a new file.

    Parameters:
    input_file_path (str): The path to the input NDJSON file.
    output_file_path (str): The path to the output file for the indented content.
    """

    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:

            for line in infile:
                pretty_json = json.dumps(json.loads(line), indent=4)
                outfile.write(pretty_json + '\n\n')

    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing JSON: {e}")

    except FileNotFoundError:
        print(f"File not found: {input_file_path}")


def process_ndjson(input_file_path: str, output_file_path : str) -> None:
    """
    Process the contents of an NDJSON file and write the results to an output file.

    Arguments:
    input_file_path -- path to the input NDJSON file.
    output_file_path -- path to the output NDJSON file.

    Raises:
    JSONDecodeError: If there is a problem parsing the file's JSON.
    FileNotFoundError: If the input file does not exist.
    """

    if is_file_empty (input_file_path):
        sys.exit (0)

    print (f"Processing {input_file_path} to {output_file_path}")

    try:
        with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
            for line in input_file:
                json_obj = json.loads(line.strip())
                if not isinstance(json_obj, dict):
                    continue

                result_data_list = transform_json(cleanUp(json_obj))

                for item in result_data_list:
                    output_file.write(json.dumps(item) + '\n')

    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing JSON: {e}\n\n", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Input file {input_file_path} not found.\n\n", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}\n\n", file=sys.stderr)
        sys.exit(1)



def sort_ndjson(input_file, output_file="/tmp/concat_sorted.ndjson", sort_key="regex"):
    """
    Sorts an ndjson file by a specified key and writes the sorted data to a new ndjson file.

    :param input_file: Path to the input ndjson file.
    :param output_file: Path to the output ndjson file.
    :param sort_key: The key to sort the ndjson objects by.
    """
    try:
        with open(input_file, 'r') as infile:
            data = [json.loads(line) for line in infile]

        sorted_data = sorted(data, key=lambda x: x.get(sort_key, ''))

        with open(output_file, 'w') as outfile:
            for item in sorted_data:
                json.dump(item, outfile)
                outfile.write('\n')

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(description='Process and clean NDJSON files.')
    parser.add_argument('InputFile', metavar='input_file', type=str, help='The path to the input NDJSON file.')
    parser.add_argument('OutputFile', metavar='output_file', type=str, help='The path for the output NDJSON file.')
    parser.add_argument('--print-only', action='store_true', help='Only print the input NDJSON file, bypassing processing.')
    parser.add_argument('--sort-only', action='store_true', help='Sort the input NDJSON file, bypassing processing.')

    args = parser.parse_args()

    if args.sort_only:
        sort_ndjson(args.InputFile, args.OutputFile)
    elif args.print_only:
        ndjson_printer(args.InputFile, args.OutputFile)
    else:
        process_ndjson(args.InputFile, args.OutputFile)

if __name__ == "__main__":
    main()
