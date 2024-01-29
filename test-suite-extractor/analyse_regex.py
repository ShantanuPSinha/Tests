import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_box_plots(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    positive_counts = []
    negative_counts = []

    for line in lines:
        data = json.loads(line)
        # Ensure count is non-zero before applying log
        if data['positive_inputs']:
            positive_counts.append(len(data['positive_inputs']))
        if data['negative_inputs']:
            negative_counts.append(len(data['negative_inputs']))

    # Check if there's data to plot
    if not positive_counts or not negative_counts:
        print("No data to plot. Please check the file.")
        return

    # Seaborn style
    sns.set(style="whitegrid")

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))

    # Box plot for positive inputs
    sns.boxplot(y=np.log1p(positive_counts), ax=axs[0], color='lightblue', width=0.5, whis=1.5)
    axs[0].set_title('Distribution of Positive Inputs Count (Log Scale)')
    axs[0].set_xlabel('Positive Inputs')
    axs[0].set_ylabel('Log Count')
    axs[0].yaxis.set_minor_locator(plt.AutoMinorLocator())
    axs[0].grid(which='minor', linestyle=':', linewidth='0.5', color='gray')

    # Box plot for negative inputs
    sns.boxplot(y=np.log1p(negative_counts), ax=axs[1], color='salmon', width=0.5, whis=1.5)
    axs[1].set_title('Distribution of Negative Inputs Count (Log Scale)')
    axs[1].set_xlabel('Negative Inputs')
    axs[1].set_ylabel('Log Count')
    axs[1].yaxis.set_minor_locator(plt.AutoMinorLocator())
    axs[1].grid(which='minor', linestyle=':', linewidth='0.5', color='gray')

    plt.suptitle('Box and Whisker Plots for Positive and Negative Inputs (Log Scale)')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to fit suptitle
    plt.show()

generate_box_plots('/home/shantanu/duality/Tests/test-suite-extractor/output_file.json')
