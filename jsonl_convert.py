#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
import tempfile
import logging
import subprocess
import sys


# --- Configuration ---
DATASET_ROOT = Path('dataset')
OUTPUT_FILE = Path('dcp-bench-open.jsonl')

# Log file for warnings and errors during conversion
LOG_FILE = Path('jsonl_conversion.log')
# --- End Configuration ---

# --- Setup Logging ---
# Configure logging to write to a file and print info messages to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'), # Overwrite log file each run
        logging.StreamHandler() # Also print logs to console
    ]
)
# ---

def extract_metadata(content: str) -> list[str]:
    # extract metadata: all non-empty lines until the first multi-line comment
    metadata = []
    i = 0
    lines = content.splitlines()
    while i < len(lines) and not lines[i].startswith('"""'):
        metadata.append(lines[i].strip())
        i += 1
    # Remove any leading/trailing whitespace and empty lines
    metadata = [line for line in metadata if line]
    return metadata

def extract_description(content: str, filepath: Path) -> str:
    # extract problem description: In the first multi-line comment.
    # Use regex to find the first multi-line comment
    multi_line_comment_pattern = re.compile(r'"""(.*?)\s*"""|\'\'\'(.*?)\s*\'\'\'', re.DOTALL)
    lines = content.splitlines()
    match = multi_line_comment_pattern.search(" ".join(lines))

    if match:
        # Extract the comment content
        problem_description = match.group(0).strip('"""').strip("'''").strip()
    else:
        raise ValueError("Problem description not found in the script content")

    # Check if the description is empty or contains only whitespace
    if not problem_description or problem_description.isspace():
        logging.warning(f"[{filepath.name}] Extracted description is empty or contains only whitespace.")
        return ""

    return problem_description

def extract_dec_vars(description: str) -> list[str]:
    # Extract decision variables from the description
    # They are in parentheses of the last line of the description (after the word "Print" is mentioned)
    # they could be either all in the same par (e.g. (x,y,z)) or in different ones (e.g. (x), (y), (z))

    # Find where the last Print statement is
    print_index = description.rfind("Print")
    if print_index == -1:
        logging.warning("No 'Print' statement found in the description.")
        return []

    # Extract the substring after the last Print statement
    decision_vars_str = description[print_index + len("Print"):].strip()
    # Find all parentheses in the substring
    parentheses_pattern = re.compile(r'\((.*?)\)')
    matches = parentheses_pattern.findall(decision_vars_str)
    decision_vars = []
    for match in matches:
        # Split the variables by comma and strip whitespace
        vars_in_parentheses = [var.strip() for var in match.split(',')]
        decision_vars.extend(vars_in_parentheses)
    # Remove duplicates and strip whitespace
    decision_vars = list(set(var.strip() for var in decision_vars if var.strip()))
    # Check if the decision variables are empty or contain only whitespace
    if not decision_vars:
        logging.warning("Extracted decision variables are empty or contain only whitespace.")
        return []

    # sort for consistency
    decision_vars.sort()

    # Return the list of decision variables
    return decision_vars


def extract_input_data(content: str):
    """
    Parses a string of Python variable assignments into a dictionary.
    """
    # Input Data: between # Data and # End of data
    # Use regex to find the input data
    input_data_pattern = re.compile(r'# Data(.*?)# End of data', re.DOTALL | re.IGNORECASE)
    lines = content.splitlines()
    match = input_data_pattern.search("\n".join(lines))

    if match:
        # Extract the input data
        input_data = match.group(1).strip()
    else:
        return "", {}

    # This dictionary will store the variables after the code is executed
    input_data_json = {}
    try:
        # Execute the code string.
        exec(input_data, {}, input_data_json)
    except Exception as e:
        logging.error(f"Error executing input data string: {e}")
        return input_data, {}
    return input_data, input_data_json


def extract_cpmpy_code(content: str) -> str:
    multi_line_comment_pattern = re.compile(r'"""(.*?)\s*"""|\'\'\'(.*?)\s*\'\'\'', re.DOTALL)
    match = multi_line_comment_pattern.search(content)

    if match:
        # Extract the comment content
        content_after_description = content[match.end():].strip()
    else:
        raise ValueError("Content after description not found in the script content")
    return content_after_description


def extract_cpmpy_code_no_data(content: str) -> str:
    # return everything after the first import

    content_no_data = extract_cpmpy_code(content)
    # remove everything between # Data and # End of data
    input_data_pattern = re.compile(r'# Data(.*?)# End of data', re.DOTALL | re.IGNORECASE)
    content_no_data = input_data_pattern.sub('', content_no_data).strip()
    return content_no_data


def exec_code(code: str, timeout=10):
    with tempfile.TemporaryDirectory() as temp_dir:
        suffix = '.__hidden_py__'
        temp_instance_path = os.path.join(temp_dir, f"script{suffix}")
        with open(temp_instance_path, 'w', encoding='utf-8') as temp_file:
            temp_file.write(code)

        try:
            command = [sys.executable, temp_instance_path]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                cwd=temp_dir
            )
            successfully_executed = (result.returncode == 0)
            output = result.stdout if successfully_executed else result.stderr
            timeout_occurred = False

        except subprocess.TimeoutExpired:
            successfully_executed = False
            output = f"Timeout Error: Execution time exceeded {timeout} seconds"
            timeout_occurred = True
        except Exception as e:
            successfully_executed = False
            output = f"Error: {e}"
            timeout_occurred = False

    return successfully_executed, output, timeout_occurred


def extract_example_solution(content: str) -> str:
    # run the model and return the output
    successfully_executed, output, timeout_occurred = exec_code(content, timeout=10)
    assert successfully_executed, "Model execution failed"
    assert not timeout_occurred, "Model execution timed out"
    return output


def extract_all_instances(filepath):
    # look for the .json file of the same name in the same directory
    problem_name = filepath.stem.replace('.cpmpy', '')
    json_filepath = filepath.parent / f"{problem_name}.json"
    if not json_filepath.is_file():
        print(f"No JSON file found for {filepath.name}, skipping all_instances extraction.")
        return []
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            all_instances = json.load(f)
        return all_instances
    except Exception as e:
        logging.error(f"[{filepath.name}] Error reading JSON file {json_filepath.name}: {e}")
        return []


def process_file(filepath: Path) -> dict | None:
    """
    Processes a single Python file: reads content and extracts all fields.

    Args:
        filepath: Path object for the Python file.

    Returns:
        A dictionary containing the extracted data, or None if reading fails.
    """
    logging.info(f"Processing file: {filepath}")
    try:
        # Read file content, trying common encodings
        try:
            content = filepath.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            logging.warning(f"[{filepath.name}] UTF-8 decoding failed, trying latin-1.")
            content = filepath.read_text(encoding='latin-1')

    except Exception as e:
        logging.error(f"[{filepath.name}] Error reading file: {e}")
        return None

    # Extract ID from filename (e.g., "csplib_028_bibd.cpmpy.py" -> "csplib_028_bibd")
    instance_id = filepath.stem.replace('.cpmpy', '')

    # Extract all components
    metadata = extract_metadata(content)
    description = extract_description(content, filepath)
    decision_variables = extract_dec_vars(description)
    input_data, input_data_json = extract_input_data(content)
    cp_model = extract_cpmpy_code(content)
    example_solution = extract_example_solution(cp_model)
    all_instances = extract_all_instances(filepath)


    # matching between decision variables and example solution's keys
    # parse the example solution as json from string
    try:
        example_solution = json.loads(example_solution)
    except json.JSONDecodeError as e:
        logging.error(f"[{filepath.name}] Error decoding example solution JSON: {e}")
        example_solution = {}

    # Check if the keys in example solution and decision variables match exactly
    if set(example_solution.keys()) != set(decision_variables):
        logging.warning(f"[{filepath.name}] Decision variables and example solution keys do not match.")
        # Optionally, you can raise an error or handle it as needed
        # raise ValueError("Decision variables and example solution keys do not match.")

    # --- Data Validation ---
    if not description:
         logging.warning(f"[{filepath.name}] Extracted description is empty.")
    if not cp_model:
         logging.warning(f"[{filepath.name}] Extracted CPMpy code is empty.")
    # ---

    # Assemble the final dictionary for this file
    return {
        "id": instance_id,
        "metadata": metadata,
        "description": description,
        "example_instance": input_data,
        # "instances": [input_data_json],
        "instances": all_instances,
        "model": extract_cpmpy_code_no_data(content),
        # "model": cp_model,
        "example_solution": example_solution,
        "decision_variables": decision_variables,
    }


def main():
    processed_count = 0
    error_count = 0

    # Ensure the dataset root directory exists
    if not DATASET_ROOT.is_dir():
        logging.error(f"Dataset root directory '{DATASET_ROOT}' not found or is not a directory.")
        print(f"Error: Dataset root directory '{DATASET_ROOT}' not found.")
        print("Please ensure the script is run from the correct location or update the DATASET_ROOT variable.")
        return

    logging.info(f"Starting conversion process.")
    logging.info(f"Dataset Root: {DATASET_ROOT.resolve()}")
    logging.info(f"Output File: {OUTPUT_FILE.resolve()}")
    logging.info(f"Log File: {LOG_FILE.resolve()}")

    # Open the output file in write mode (clears existing file)
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
            # Iterate through all .cpmpy.py files in the dataset directory recursively
            for filepath in DATASET_ROOT.rglob("*.cpmpy.py"):
                data = process_file(filepath)
                if data:
                    try:
                        # Convert the dictionary to a JSON string
                        json_line = json.dumps(data, ensure_ascii=False)
                        # Write the JSON string as a single line to the output file
                        outfile.write(json_line + '\n')
                        processed_count += 1
                    except Exception as e:
                        logging.error(f"[{filepath.name}] Error writing JSON line: {e}")
                        error_count += 1
                else:
                    # process_file already logged the read error
                    error_count += 1

    except IOError as e:
        logging.error(f"Could not open or write to output file {OUTPUT_FILE}: {e}")
        print(f"Error: Could not write to output file {OUTPUT_FILE}. Check permissions.")
        return
    except Exception as e:
         logging.error(f"An unexpected error occurred during processing: {e}")
         print(f"An unexpected error occurred. Check {LOG_FILE} for details.")
         return

    # validate that all ids are unique
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as outfile:
        ids = set()
        for line in outfile:
            try:
                data = json.loads(line)
                instance_id = data.get("id")
                if instance_id in ids:
                    logging.error(f"Duplicate instance ID found: {instance_id}")
                else:
                    ids.add(instance_id)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON line during ID uniqueness check: {e}")

    # --- Final Summary ---
    summary_message = f"Conversion finished. Processed: {processed_count}, Errors/Skipped: {error_count}."
    logging.info(summary_message)
    print(f"\n{summary_message}")
    print(f"Output written to: '{OUTPUT_FILE.resolve()}'")
    print(f"Detailed logs available in: '{LOG_FILE.resolve()}'")
    # ---

if __name__ == "__main__":
    main()
