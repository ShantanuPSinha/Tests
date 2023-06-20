import json
import os

class datasetInterface:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = self.read_data()
        self.current_index = 0

    def read_data(self):
        with open(self.file_name, 'r') as file:
            data = json.load(file)
        return data

    def save_data(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.data, file, indent=4)

    def write_data (self, outfilename="Dataset_test.json"):
        with open(outfilename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_dataset(self, dataset_name, description, tasks):
        entry = {}
        entry["Dataset Name"] = dataset_name
        entry["Description"] = description
        entry["Tasks"] = tasks

        self.data["Datasets"].append(entry)

    def add_tasks (self, dataset_name, positive_examples, negative_examples, ground_truth=""):
        # Find the dataset with the given name
        dataset = None
        for entry in self.data["Datasets"]:
            if entry["Dataset Name"] == dataset_name:
                dataset = entry
                break

        if dataset is None:
            print(f"Dataset '{dataset_name}' not found.")
            return
        
        task = {}
        task["positiveExamples"] = positive_examples
        task["negativeExamples"] = negative_examples
        task["groundTruth"] = ground_truth

        dataset["Tasks"].append(task)
        return

    def datasets(self):
        dataset_names = []
        for dataset in self.data["Datasets"]:
            dataset_names.append(dataset["Dataset Name"])
        return dataset_names
    
    def get_tasks_from_dataset(self, dataset_name, index=0, num_tasks=1):
        if num_tasks < 1 or index < 0:
            return None
        
        for dataset in self.data["Datasets"]:
            if dataset["Dataset Name"] == dataset_name:
                tasks = dataset["Tasks"]
                tasks_count = len(tasks)
                if tasks_count > 0 and 0 <= index < tasks_count:
                    end_index = min(index + num_tasks, tasks_count)
                    tasks = tasks[index:end_index]
                    task_tuples = []
                    for task in tasks:
                        positive_examples = task["positiveExamples"]
                        negative_examples = task["negativeExamples"]
                        ground_truth = task["groundTruth"]
                        if (num_tasks == 1):
                            return positive_examples, negative_examples, ground_truth
                        task_tuples.append((positive_examples, negative_examples, ground_truth))
                    return task_tuples
    
        # If dataset_name is not found or index is out of range, return an empty list
        return None
    
    def generate_rfixer_testcase (self, outfilepath, task):
        positive_examples = task[0]
        negative_examples = task[1]
        with open(outfilepath, 'w') as outfile:
            outfile.write(f"{positive_examples[0]}|{negative_examples[0]}\n+++\n")
            outfile.write('\n'.join(positive_examples))
            outfile.write('\n---\n')
            outfile.write('\n'.join(negative_examples))

    def generate_gen_test (self, task, task_name):
        task_dir = "genetic_testcases/" + task_name
        os.makedirs(task_dir)
        positive_examples = task[0]
        negative_examples = task[1]

        with open(task_dir + "/left.txt", 'w') as outfile:
            outfile.write('\n'.join(positive_examples))

        with open(task_dir + "/right.txt", 'w') as outfile:
            outfile.write('\n'.join(negative_examples))


interface = datasetInterface('/home/shantanu/duality/eval-RFixer/Datasets/dataset.json')
