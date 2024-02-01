import json, sys, time, os, re
import matplotlib.pyplot as plt
import numpy as np

from run_rfixer import run_rfixer, generate_RFixer_input

def generate_percentile_plots(positive_inputs, negative_inputs):
    percentiles = np.arange(5, 101, 5)

    def plot_percentiles(ax, inputs, color, title):
        lengths = [length for _, length in inputs]
        percentile_values = np.percentile(lengths, percentiles)
        ax.set_title(title)
        ax.set_xlabel('Percentile')
        ax.set_ylabel('Input Length')
        ax.plot(percentiles, percentile_values, marker='o', linestyle='-', color=color)
        ax.set_yscale('log')

        # Add gridlines
        major_ticks = np.arange(0, 101, 10)
        minor_ticks = np.arange(0, 101, 5)
        ax.set_xticks(major_ticks)
        ax.set_xticks(minor_ticks, minor=True)
        ax.grid(which='major', alpha=0.5)
        ax.grid(which='minor', axis='x', alpha=0.2)

        for i, value in enumerate(percentile_values):
            ax.annotate(f"{value:.0f}", (percentiles[i], value), textcoords="offset points", xytext=(0,10), ha='center')

    _, axs = plt.subplots(1, 2, figsize=(12, 6))
    plot_percentiles(axs[0], positive_inputs, 'blue', 'Positive Input Lengths')
    plot_percentiles(axs[1], negative_inputs, 'red', 'Negative Input Lengths')
    plt.tight_layout()

    filename = 'percentile_plots.png'
    counter = 1

    while os.path.exists(filename):
        filename = f'percentile_plots_{counter}.png'
        counter += 1

    plt.savefig(filename)
    print(f"Saved percentile plots to {filename}")

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper


def dump_to_ndjson(data, file_name=".temp_sols.ndjson"):
    with open(file_name, 'w') as file:
        if isinstance(data, dict):
            for key, value in data.items():
                json_object = json.dumps({key: value})
                file.write(json_object + '\n')
        elif isinstance(data, list):
            for json_obj in data:
                file.write(json.dumps(json_obj) + '\n')
        else:
            raise ValueError("Data must be either a dictionary or a list of dictionaries")

def load_data(file_path: str):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    positive_inputs = []
    negative_inputs = []
    data = []

    for id, line in enumerate(lines):
        entry = json.loads(line)
        positive_len = len(entry['positive_inputs'])
        negative_len = len(entry['negative_inputs'])
        positive_inputs.append((id, positive_len))
        negative_inputs.append((id, negative_len))
        entry['id'] = id  # Add an ID field
        data.append(entry)

    return positive_inputs, negative_inputs, data

"""
Not sure if this is useful. Need both positive and negative inputs for synthesis to work.
Grabbing unequal number of positive and negative inputs might not be useful.
"""
def find_entries_in_percentile_range(data, input_data, lower_percentile, upper_percentile, mode):
    # Just so I remember what list I've passed in
    if mode not in ['positive', 'negative']:
        raise ValueError("Mode must be 'positive' or 'negative'")

    lengths = [length for _, length in input_data]
    lower_bound = np.percentile(lengths, lower_percentile)
    upper_bound = np.percentile(lengths, upper_percentile)

    entries_in_range = []
    for id, length in input_data:
        if lower_bound <= length <= upper_bound:
            entries_in_range.append(id)

    return entries_in_range

def filter_entries(positive_inputs, negative_inputs, data, upper_bound=100, lower_bound=5):
    positive_dict = {id: length for id, length in positive_inputs}
    negative_dict = {id: length for id, length in negative_inputs}

    filtered_positive_inputs = []
    filtered_negative_inputs = []
    filtered_data = []

    for entry in data:
        id = entry['id']
        pos_len = positive_dict.get(id, 0)
        neg_len = negative_dict.get(id, 0)
        if (lower_bound < pos_len < upper_bound) and (lower_bound < neg_len < upper_bound):
            filtered_data.append(entry)
            filtered_positive_inputs.append((id, pos_len))
            filtered_negative_inputs.append((id, neg_len))

    return filtered_positive_inputs, filtered_negative_inputs, filtered_data


# Define a function to load the NDJSON file into a dictionary
def load_ndjson_as_dict(file_path):
    data_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    # Parse each line as a JSON object and use a unique identifier as the key
                    json_obj = json.loads(line)
                    # Assuming the first key-value pair in each JSON object is the identifier
                    key = list(json_obj.keys())[0]
                    data_dict[key] = json_obj[key]
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse line as JSON: {line}")
                except KeyError:
                    print(f"Warning: Key not found in line: {line}")
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except Exception as e:
        print(f"Error: {e}")

    return data_dict

INFILE = sys.argv[1] if len(sys.argv) > 1 else './regex.ndjson'
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else './output'
UPPER_BOUND = float ('inf')
LOWER_BOUND = 2

positive_lengths, negative_lengths, data = load_data(INFILE)
filtered_positive_inputs, filtered_negative_inputs, filtered_data = filter_entries(positive_lengths, negative_lengths, data, UPPER_BOUND, LOWER_BOUND)

print (f'Total Packages {len (filtered_data)}')

generate_RFixer_input(filtered_data, OUTDIR)
solutions = run_rfixer(OUTDIR, True, timeout=20)
dump_to_ndjson (solutions)

for id, solution in solutions.items():
    data [int(id)]['RFixer-Solution'] = solution

dump_to_ndjson (data, "rfixer_solutions.ndjson")
