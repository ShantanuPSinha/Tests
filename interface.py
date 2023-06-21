"""
Interface for interacting a with JSON dataset
"""

# Shantanu Sinha

import json
import jsonschema
import os


class datasetInterface:
    """
    A class representing a dataset interface to manage datasets and tasks.

    Args:
        file_name (str): The name of the JSON file to read and save the data.

    Attributes:
        file_name (str): The name of the JSON file.
        data (dict): The dataset data loaded from the JSON file.

    Methods:
        TODO

    """
    def __init__(self, file_name : str):
        self.file_name = file_name
        self.data = self.read_data()
        self.validateJSON()
        self.current_index = 0

    def read_data(self):
        """
        Read the dataset data from the JSON file.

        Returns:
            dict: The dataset data loaded from the JSON file.

        """
        with open(self.file_name, 'r') as file:
            data = json.load(file)
        return data

    def save_data(self):
        """
        Save the dataset data to the same JSON file.
        WARNING: MODIFIES THE ORIGINAL DATASET FILE

        Returns:
            None

        """
        with open(self.file_name, 'w') as file:
            json.dump(self.data, file, indent=4)

    def write_data(self, outfilename="Dataset_test.json"):
        """
        Write the dataset data to a different JSON file.

        Args:
            outfilename (str, optional): The name of the output JSON file. Defaults to "Dataset_test.json".

        Returns:
            None

        """
        with open(outfilename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def add_dataset(self, dataset_name : str, description = "", tasks = []):
        """
        Add a new dataset entry to the dataset data.

        Args:
            dataset_name (str): The name of the dataset.
            description (str): The description of the dataset.
            tasks (list): A list of tasks associated with the dataset.

        Returns:
            None

        """

        entry = {}
        entry["Dataset Name"] = dataset_name
        entry["Description"] = description
        entry["Tasks"] = tasks

        self.data["Datasets"].append(entry)

    def add_tasks(self, dataset_name:str, positive_examples:list, negative_examples:list, ground_truth=""):
        """
        Add tasks to an existing dataset.

        Args:
            dataset_name (str): The name of the dataset to add tasks to.
            positive_examples (list): A list of positive examples for the tasks.
            negative_examples (list): A list of negative examples for the tasks.
            ground_truth (str, optional): The ground truth information for the tasks. Defaults to an empty string.

        Returns:
            None

        """
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
        """
        Retrieve a list of dataset names.

        Returns:
            list: A list of dataset names.

        """
        dataset_names = []
        for dataset in self.data["Datasets"]:
            dataset_names.append(dataset["Dataset Name"])
        return dataset_names

    
    def get_task (self, dataset_name:str, index=0, num_tasks=1):
        """
        Get task(s) from a specific dataset.

        Args:
            dataset_name (str): The name of the dataset to retrieve the task(s) from.
            index (int, optional): The starting index of the task(s) to retrieve. Defaults to 0.
            num_tasks (int, optional): The number of tasks to retrieve. Defaults to 1.

        Returns:
            list or tuple or None:  If a single task is retrieved, a tuple containing positive examples, negative examples, and ground truth is returned.
                                    If multiple tasks are retrieved, a list of tuples is returned, where each tuple represents a task.
                                    If no tasks are found or invalid input is provided, None is returned.
        """

        if num_tasks < 1 or index < 0:
            return None

        for dataset in self.data.get("Datasets", []):
            if dataset.get("Dataset Name") == dataset_name:
                tasks = dataset.get("Tasks", [])
                tasks_count = len(tasks)
                if index >= tasks_count:
                    return None

                end_index = min(index + num_tasks, tasks_count)
                tasks = tasks[index:end_index]

                if num_tasks == 1:
                    task = tasks[0]
                    return ([
                        task.get("positiveExamples", []),
                        task.get("negativeExamples", []),
                        task.get("groundTruth", [])
                    ])

                task_tuples = []
                for task in tasks:
                    positive_examples = task.get("positiveExamples", [])
                    negative_examples = task.get("negativeExamples", [])
                    ground_truth = task.get("groundTruth", [])
                    task_tuples.append((positive_examples, negative_examples, ground_truth))

                return task_tuples

        return None

    def generate_rfixer_testcase (self, outfilepath:str, task):
        """
        Generate an RFixer testcase file.

        Args:
            outfilepath (str): Path to the output file to be created.
            task (dict): The task containing positive and negative examples.

        Returns:
            None
    
        """
        positive_examples = task["positiveExamples"]
        negative_examples = task["negativeExamples"]
        with open(outfilepath, 'w') as outfile:
            outfile.write(f"{positive_examples[0]}|{negative_examples[0]}\n+++\n")
            outfile.write('\n'.join(positive_examples))
            outfile.write('\n---\n')
            outfile.write('\n'.join(negative_examples))


    def generate_gen_test (self, task, task_name):
        """
        Generate test cases for genetic synthesis for a given task and task name.

        Args:
            task (dict): The task containing positive and negative examples.
            task_name (str): The name of the task to generate test cases for.

        Returns:
            None
        """

        task_dir = "genetic_testcases/" + task_name       
        os.makedirs(task_dir, exist_ok=True)
        positive_examples = task["positiveExamples"]
        negative_examples = task["negativeExamples"]

        with open(task_dir + "/left.txt", 'w') as outfile:
            outfile.write('\n'.join(positive_examples))

        with open(task_dir + "/right.txt", 'w') as outfile:
            outfile.write('\n'.join(negative_examples))

    

    def get_dataset(self, dataset_name:str):
        """
        Retrieve the tasks associated with a specific dataset.

        Args:
            dataset_name (str): The name of the dataset to retrieve.

        Returns:
            list or None: A list of tasks associated with the dataset if found, otherwise None.

        """

        for dataset in self.data.get("Datasets", []):
            if dataset.get("Dataset Name") == dataset_name:
                return dataset.get("Tasks", [])
        return None

    

    def tasks (self):
        """
        Iterate over every task in every dataset. Get all tasks across every dataset.

        Yields:
            dict: A task dictionary containing positiveExamples, negativeExamples, and groundTruth.

        """
        for dataset in self.data.get("Datasets", []):
            for task in dataset.get("Tasks", []):
                yield task


    def validate_schema_individual(self):
        """
        Validates the individual dataset schema.

        Returns:
            bool: True if the schema is valid, False otherwise.
        """
        individual_dataset_schema = {
            "$schema": "http://json-schema.org/schema#",
            "type": "object",
            "properties": {
                "Dataset Name": {
                    "type": "string"
                },
                "Description": {
                    "type": "string"
                },
                "Tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "positiveExamples": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "negativeExamples": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "groundTruth": {
                                "type": ["array", "string"]
                            }
                        },
                        "required": [
                            "groundTruth",
                            "negativeExamples",
                            "positiveExamples"
                        ]
                    }
                }
            },
            "required": [
                "Dataset Name",
                "Description",
                "Tasks"
            ]
        }

        try:
            jsonschema.validate(self.data, individual_dataset_schema)
            return True
        except jsonschema.ValidationError:
            return False

    def validate_schema_dataset(self):
        """
        Validates the dataset schema.

        Returns:
            bool: True if the schema is valid, False otherwise.
        """
        bigDatasetSchema = {
            "type": "object",
            "properties": {
                "Datasets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Dataset Name": {
                                "type": "string"
                            },
                            "Description": {
                                "type": "string"
                            },
                            "Tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "positiveExamples": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "negativeExamples": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "groundTruth": {
                                            "type": [
                                                "array",
                                                "string"
                                            ]
                                        }
                                    },
                                    "required": [
                                        "groundTruth",
                                        "negativeExamples",
                                        "positiveExamples"
                                    ]
                                }
                            }
                        },
                        "required": [
                            "Dataset Name",
                            "Description",
                            "Tasks"
                        ]
                    }
                }
            },
            "required": [
                "Datasets"
            ]
        }

        try:
            jsonschema.validate(self.data, bigDatasetSchema)
            return True
        except jsonschema.ValidationError:
            return False

    def validateJSON(self):
        """
        Validates the dataset against two schemas.

        Raises:
            AssertionError: If the dataset schema is invalid.
        """
        if self.validate_schema_dataset() or self.validate_schema_individual():
            return

        raise AssertionError("Invalid Dataset Schema")
    

    def search_by_gt (self, gt:str):
        """
        Find tasks in the dataset that match a given ground truth value.

        Args:
            gt: The ground truth value to search for. Ground Truth must be a string. If you have an array of Ground Truth values, search one-by-one

        Returns:
            list: A list of tasks that match the given ground truth value.

        """

        matching_tasks = []

        for task in self.tasks():
            if task.get("groundTruth") == gt:
                matching_tasks.append(task)
        return matching_tasks
    

__all__ = ["datasetInterface"]