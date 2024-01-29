import json
import matplotlib.pyplot as plt
import numpy as np

def load_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    positive_inputs = []
    negative_inputs = []

    for line in lines:
        data = json.loads(line)
        positive_inputs.append(len(data['positive_inputs']))
        negative_inputs.append(len(data['negative_inputs']))

    return sorted(positive_inputs), sorted(negative_inputs)

def annotate_plot(ax, x, y):
    for i in range(len(x)):
        ax.annotate(f"{y[i]:.0f}", (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

def generate_percentile_plots(file_path):
    positive_lengths, negative_lengths = load_data(file_path)

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

generate_percentile_plots('/home/shantanu/duality/Tests/test-suite-extractor/output_file.ndjson')
