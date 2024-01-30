import json, sys, time
import matplotlib.pyplot as plt
import numpy as np

# Cause why not at this point
def timing_wrapper(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

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

    # Sort by the length while keeping the IDs
    positive_inputs.sort(key=lambda x: x[1])
    negative_inputs.sort(key=lambda x: x[1])

    return positive_inputs, negative_inputs, data


def annotate_plot(ax, x : np.ndarray, y : np.ndarray):
    for i in range(len(x)):
        ax.annotate(f"{y[i]:.0f}", (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')


def generate_percentile_plots(positive_inputs : list, negative_inputs : list) -> None:
    positive_lengths = [length for _, length in positive_inputs]
    negative_lengths = [length for _, length in negative_inputs]

    percentiles = np.arange(5, 101, 5)
    positive_percentile_values = np.percentile(positive_lengths, percentiles)
    negative_percentile_values = np.percentile(negative_lengths, percentiles)

    _, axs = plt.subplots(1, 2, figsize=(12, 6))

    major_ticks = np.arange(0, 101, 10)
    minor_ticks = np.arange(0, 101, 5)

    for ax in axs:
        ax.set_xticks(major_ticks)
        ax.set_xticks(minor_ticks, minor=True)
        
        ax.grid(which='major', alpha=0.5)
        ax.grid(which='minor', axis='x', alpha=0.2)

    # Positive Inputs Plot
    axs[0].set_title('Percentile Plot of Positive Input Lengths')
    axs[0].set_xlabel('Percentile')
    axs[0].set_ylabel('Input Length')
    axs[0].plot(percentiles, positive_percentile_values, marker='o', linestyle='-', color='blue')
    axs[0].set_yscale('log')
    annotate_plot(axs[0], percentiles, positive_percentile_values)

    # Negative Inputs Plot
    axs[1].set_title('Percentile Plot of Negative Input Lengths')
    axs[1].set_xlabel('Percentile')
    axs[1].set_ylabel('Input Length')
    axs[1].plot(percentiles, negative_percentile_values, marker='o', linestyle='-', color='red')
    axs[1].set_yscale('log')
    annotate_plot(axs[1], percentiles, negative_percentile_values)

    plt.tight_layout()
    plt.savefig('percentile_plots.png')

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
            entries_in_range.append(data[id])

    return entries_in_range

def filter_non_zero_entries(positive_inputs, negative_inputs, data):
    positive_dict = {id: length for id, length in positive_inputs}
    negative_dict = {id: length for id, length in negative_inputs}

    filtered_positive_inputs = []
    filtered_negative_inputs = []
    filtered_data = []

    for entry in data:
        id = entry['id']
        if len(entry['positive_inputs']) > 0 and len(entry['negative_inputs']) > 0:
            filtered_data.append(entry)
            if id in positive_dict:
                filtered_positive_inputs.append((id, positive_dict[id]))
            if id in negative_dict:
                filtered_negative_inputs.append((id, negative_dict[id]))

    return filtered_positive_inputs, filtered_negative_inputs, filtered_data

positive_lengths, negative_lengths, data = load_data(sys.argv[1] if len(sys.argv) > 1 else './regex.ndjson')
generate_percentile_plots(positive_lengths, negative_lengths)
filtered_positive_inputs, filtered_negative_inputs, filtered_data = filter_non_zero_entries(positive_lengths, negative_lengths, data)

