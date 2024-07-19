import json
import csv


def json_to_csv(json_file_path, csv_file_path):
    # Read the JSON file
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

    # Ensure the data is an array of objects
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("JSON file must contain an array of objects")

    # Extract the field names from the first object
    initial_results_fields = [
        "input_example",
        "prompt_granite",
        "result_granite",
        "result_granite_goodness",
        "result_granite_commentary",
        "prompt_llama",
        "result_llama",
        "result_llama_goodness",
        "result_llama_commentary",
    ]

    instruct_lab_results_fields = [
        "input_example",
        "prompt_base_model",
        "result_base_model",
        "result_base_model_goodness",
        "result_base_model_commentary",
        "prompt_trained_model",
        "result_trained_model",
        "result_trained_model_goodness",
        "result_trained_model_commentary",
    ]

    fieldnames = (
        initial_results_fields
        if json_file_path == "initial_results.json"
        else instruct_lab_results_fields
    )

    # Write the CSV file
    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


# Example usage
json_file_path = "instructlab_results.json"  # Path to your input JSON file
csv_file_path = "instructlab_results.csv"  # Path to your output CSV file
json_to_csv(json_file_path, csv_file_path)
