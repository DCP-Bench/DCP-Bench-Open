import time
import json
import os
import subprocess
import sys
import tempfile
import click
from pathlib import Path
import minizinc
import datetime
from tqdm import tqdm

CPMPY_FRAMEWORK = "CPMpy"
MINIZINC_FRAMEWORK = "MiniZinc"
ORTOOLS_FRAMEWORK = "OR-Tools"

GT_PROBLEM_NAME_COLUMN = "id"
GT_MODEL_CODE_COLUMN = "model"
GT_EXAMPLE_INSTANCE_COLUMN = "example_instance"

SCRIPT_EXECUTION_TIMEOUT = 60  # seconds


def exec_code_minizinc(code: str, timeout_sec):
    """
    Executes a MiniZinc model string using the minizinc-python library.

    :param code: The MiniZinc model code as a string.
    :param timeout_sec: The maximum time to wait for the solver in seconds.
    :return: A tuple of (success, output, timeout_occured)
    """
    timeout_duration = datetime.timedelta(seconds=timeout_sec)

    try:
        # 1. Create a MiniZinc model instance
        model = minizinc.Model()
        model.add_string(code)

        # 2. Find a default solver configured with MiniZinc
        gecode = minizinc.Solver.lookup("gecode")
        if gecode is None:
            raise RuntimeError("No suitable solver found. Please install a MiniZinc solver.")

        # 3. Create an Instance to solve
        instance = minizinc.Instance(gecode, model)

        # 4. Solve the instance with the specified timeout
        # The solve() method handles the timeout internally.
        result = instance.solve(timeout=timeout_duration)

        # 5. Process the result
        if result.status in {minizinc.Status.SATISFIED, minizinc.Status.OPTIMAL_SOLUTION}:
            successfully_executed = True
            output = str(result.solution) if result.solution is not None else ""
            timeout_occurred = False
        elif result.status == minizinc.Status.UNKNOWN:
            successfully_executed = False
            output = f"Timeout Error: Solver stopped after {timeout_sec} seconds (Status: UNKNOWN)."
            timeout_occurred = True
        else:
            # Handle other non-success statuses (UNSAT, ERROR, etc.)
            successfully_executed = False
            output = f"Solving failed. Status: {result.status}"
            timeout_occurred = False

    except minizinc.MiniZincError as e:
        # Catch MiniZinc specific errors (e.g., syntax errors, solver not found)
        successfully_executed = False
        output = f"MiniZinc Error: {e}"
        timeout_occurred = False
    except Exception as e:
        # Catch other unexpected errors
        successfully_executed = False
        output = f"Unexpected Error during MiniZinc execution: {e}"
        timeout_occurred = False

    return successfully_executed, output, timeout_occurred


def exec_code(code: str, timeout=10, modelling_language='cpmpy'):
    """
    Execute the given code and return the output

    :param code: The code to execute as a string
    :param timeout: The maximum time to wait for the code to execute in seconds
    :param modelling_language: The language to use for execution (cpmpy, minizinc, or-tools)
    :return: A tuple of (success, output, timeout_occured)
    """

    # create a temp directory to store the temporary file
    temp_dir_name = "temp_dir_for_exec_code"
    temp_dir = os.path.join(os.getcwd(), temp_dir_name)
    os.makedirs(temp_dir, exist_ok=True)

    # write the code to a temporary file
    suffix = '.__hidden_py__' if modelling_language == CPMPY_FRAMEWORK or modelling_language == ORTOOLS_FRAMEWORK else '.mzn'
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix, dir=temp_dir,
                                     encoding='utf-8') as temp_file:
        temp_instance_path = temp_file.name
        temp_file.write(code)

    try:
        # execute the code
        if modelling_language == CPMPY_FRAMEWORK or modelling_language == ORTOOLS_FRAMEWORK:
            command = [sys.executable, temp_instance_path]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, encoding='utf-8')

            successfully_executed = (result.returncode == 0)
            output = result.stdout if successfully_executed else result.stderr
            timeout_occurred = False
        elif modelling_language == MINIZINC_FRAMEWORK:
            successfully_executed, output, timeout_occurred = exec_code_minizinc(code, timeout)
        else:
            raise ValueError(f"MODELLING_LANGUAGE not supported: {modelling_language}")

    except subprocess.TimeoutExpired as e:
        successfully_executed = False
        output = f"Timeout Error: Execution time exceeded {timeout} seconds"
        timeout_occurred = True
    except Exception as e:
        successfully_executed = False
        output = f"Error: {e}"
        timeout_occurred = False

    os.remove(temp_instance_path)

    return successfully_executed, output, timeout_occurred


def validate_submission_file(file_path: Path) -> tuple[bool, str]:
    """Validate the submission file format and content.

    Args:
        file_path: Path to the submission file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, f"File {file_path} does not exist"

    if not file_path.name.endswith('.jsonl'):
        return False, "Invalid file format. Please provide a .jsonl file"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            found_one = False
            for line_num, line in enumerate(file, 1):
                found_one = True
                try:
                    json_object = json.loads(line)
                    if not all(key in json_object for key in ["id", "model"]):
                        return False, f"Line {line_num}: Missing required keys 'id' and/or 'model'"
                except json.JSONDecodeError:
                    return False, f"Line {line_num}: Invalid JSON format"

            if not found_one:
                return False, "Empty file. Please provide a valid JSONL file"

    except Exception as e:
        return False, f"Error reading file: {str(e)}"

    return True, "File is valid"


def extract_json_from_code_output(output: str):
    try:
        start_index = output.find('{')
        end_index = output.rfind('}') + 1
        # Extract the JSON part
        json_part = output[start_index:end_index]
        return json.loads(json_part)
    except json.JSONDecodeError:
        return None


def add_constraints_as_string(solution):
    """Generate constraints as a string to be added to the original script."""
    constraints = ""
    if solution:  # Ensure solution is not None
        for key, value in solution.items():
            # Basic escaping for string values if they occur, though typically solutions are numeric/boolean
            if isinstance(value, str):
                constraints += f"\nmodel += ({key} == \"{value}\")"
            else:
                constraints += f"\nmodel += ({key} == {value})"
    return constraints


def get_modified_script(script_content, solution):
    """Add constraints to the script content and self-consistency checks."""
    constraints_str = add_constraints_as_string(solution)
    modified_script = f"{script_content}\n{constraints_str}"
    modified_script += """
# Print the absolute path of the current directory along with the script name
import os
print(os.path.abspath(__file__))

# Keep old objective
old_objective = None
if hasattr(model, 'objective_is_min') and model.objective_is_min is not None:
    old_objective = model.objective_value()

# Check self-consistency
if not model.solve():
    print('ERROR: The model is unsatisfiable with the self-consistency constraints')
else:
    print('SUCCESS: Model is consistent')

# Check if the objective value is the same
if old_objective is None:
    print('SUCCESS: No objective defined')
elif model.objective_value() != old_objective:
    print('ERROR: The objective value has changed')
else:
    print('SUCCESS: Objective value is consistent')
"""
    return modified_script


def evaluate_submission(submitted_models, summary_file_path, modelling_framw, top_lvl_temp_dir, dataset_file_path):
    # Load ground-truth dataset
    print(f"  Loading ground-truth dataset from {dataset_file_path}...", flush=True)
    try:
        # gt_dataset = load_dataset(GT_DATASET_NAME, split=dataset_version, trust_remote_code=True)
        # load jsonl
        gt_dataset = []
        with open(dataset_file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    json_obj = json.loads(line)
                    gt_dataset.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"  ERROR: Failed to parse JSON object from line: {line}. Error: {e}", flush=True)

        # for now, create a dict mapping problem name to model code with just the example instance
        ground_truth_models = {
            item[GT_PROBLEM_NAME_COLUMN]: item[GT_EXAMPLE_INSTANCE_COLUMN] + '\n' + item[GT_MODEL_CODE_COLUMN]
            for item in gt_dataset if
            GT_PROBLEM_NAME_COLUMN in item and GT_MODEL_CODE_COLUMN in item and item[GT_MODEL_CODE_COLUMN]
        }
        if not ground_truth_models: raise ValueError("No models in GT dataset.")
        print(f"  Loaded {len(ground_truth_models)} ground-truth models.", flush=True)
    except Exception as e_gt:
        print(f"  CRITICAL ERROR - Failed to load ground-truth dataset: {e_gt}", flush=True)
        with open(summary_file_path, "w") as f:
            f.write(f"CRITICAL ERROR: Failed to load ground-truth dataset.\nError: {e_gt}\n")
        return 1

    # Statistics
    total_submitted_models_that_also_exist_in_gt = 0
    models_ran_successfully = 0
    consistency_checks_passed = 0
    all_checks_passed = 0

    with (open(summary_file_path, "w", encoding="utf-8") as summary_f):

        # Iterate through submitted models
        for submitted_model in tqdm(submitted_models):
            curr_model = submitted_model[GT_MODEL_CODE_COLUMN]
            problem_name = submitted_model[GT_PROBLEM_NAME_COLUMN]

            print(f"\n  Processing model: {problem_name}", flush=True)
            summary_f.write(f"\n--- Model: {problem_name} ---\n")

            if problem_name in ground_truth_models:
                total_submitted_models_that_also_exist_in_gt += 1
                summary_f.write(f"    0. Found ground-truth model for '{problem_name}' in dataset.\n")
            else:
                summary_f.write(f"      - SKIPPED: Ground-truth model for '{problem_name}' not found in dataset.\n")
                continue

            summary_f.write("    1. Running submitted model...\n")
            succ_exec, output, timeout_occurred = exec_code(curr_model, timeout=SCRIPT_EXECUTION_TIMEOUT,
                                                            modelling_language=modelling_framw)

            if succ_exec:
                models_ran_successfully += 1
                summary_f.write("      - SUCCESS: Model executed successfully.\n")

            if timeout_occurred:
                summary_f.write(f"      - TIMEOUT: Execution time exceeded {SCRIPT_EXECUTION_TIMEOUT} seconds.\n")
                continue
            if not succ_exec:
                summary_f.write(f"      - FAILED: Execution failed with error: {output}\n")
                continue
            if output is None or not output.strip():
                summary_f.write(f"      - FAILED: No output from execution.\n")
                continue
            # Attempt to extract JSON from stdout
            generated_solution = extract_json_from_code_output(output)
            if generated_solution is None:
                summary_f.write(f"      - FAILED: Could not extract JSON solution from output: {output}\n")
                continue
            summary_f.write(f"      - SUCCESS: Got solution: {generated_solution}\n")

            summary_f.write("    2. Performing solution check on ground-truth model...\n")
            modified_gt_script = get_modified_script(ground_truth_models[problem_name], generated_solution)
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8',
                                                 dir=top_lvl_temp_dir) as tmp_file:
                    tmp_file.write(modified_gt_script)
                    tmp_file_path_str = tmp_file.name

                gt_check_result = subprocess.run(
                    [sys.executable, tmp_file_path_str],
                    capture_output=True, text=True, timeout=SCRIPT_EXECUTION_TIMEOUT, encoding='utf-8',
                )
                os.unlink(tmp_file_path_str)

                gt_stdout = gt_check_result.stdout
                if "SUCCESS: Model is consistent" in gt_stdout:
                    summary_f.write("      - CONSISTENCY: PASSED\n")
                    consistency_checks_passed += 1
                else:
                    summary_f.write(
                        "      - CONSISTENCY: FAILED, stdout: " + gt_stdout + "\nstderr: " + gt_check_result.stderr + "\n")
                    continue

                if "SUCCESS: Model is consistent" in gt_stdout and (
                        "SUCCESS: No objective defined" in gt_stdout or "SUCCESS: Objective value is consistent" in gt_stdout):
                    summary_f.write("      - OBJECTIVE CHECK: PASSED fully\n")
                    all_checks_passed += 1
                else:
                    summary_f.write(
                        "      - OBJECTIVE CHECK: FAILED, stdout: " + gt_stdout + "\nstderr: " + gt_check_result.stderr + "\n")

            except Exception as e_gt_run:
                summary_f.write(f"      - CHECK: FAILED (Error: {e_gt_run})\n")

        # Final statistics (write to summary_f)
        summary_f.write("\n" + "=" * 30 + "\n")
        summary_f.write("Overall Evaluation Statistics:\n")
        summary_f.write(
            f"  Total Submitted Models that also exist in the dataset: {total_submitted_models_that_also_exist_in_gt}\n")
        summary_f.write(
            f"  Models That Ran Successfully (out of submitted models): {models_ran_successfully}/{total_submitted_models_that_also_exist_in_gt}\n")
        summary_f.write(
            f"  Submission coverage perc: {float(total_submitted_models_that_also_exist_in_gt) / len(ground_truth_models) * 100:.2f}%\n")
        summary_f.write(
            f"  Error perc: {float(total_submitted_models_that_also_exist_in_gt - models_ran_successfully) / float(total_submitted_models_that_also_exist_in_gt) * 100:.2f}%\n")
        summary_f.write(f"  Consistency perc: {consistency_checks_passed / len(ground_truth_models) * 100:.2f}%\n")
        summary_f.write(f"  Final Solution Accuracy perc: {all_checks_passed / len(ground_truth_models) * 100:.2f}%\n")
        summary_f.write(
            f"  Final Solution Accuracy perc (considering only submitted models): {all_checks_passed / total_submitted_models_that_also_exist_in_gt * 100:.2f}%\n")
        summary_f.write("-" * 30 + "\n")


@click.command()
@click.option('--dataset_file', required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='Path to the ground-truth dataset JSONL file')
@click.option('--test_file', required=True,
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help='Path to the submission JSONL file')
@click.option('--modelling_framework', required=True,
              type=click.Choice([CPMPY_FRAMEWORK, ORTOOLS_FRAMEWORK, MINIZINC_FRAMEWORK]),
              help='Modelling framework used in the submission')
def main(dataset_file: Path, test_file: Path, modelling_framework: str):
    """Evaluate a file containing generated models against a ground-truth dataset."""

    is_valid, message = validate_submission_file(test_file)
    if not is_valid:
        click.echo(f"Error: {message}")
        return

    click.echo("Starting evaluation...")

    # load generated models from jsonl to memory
    print(f"  Loading models from file...", flush=True)
    submitted_models = []
    with open(test_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                json_obj = json.loads(line)
                submitted_models.append(json_obj)
            except json.JSONDecodeError as e:
                print(f"  ERROR: Failed to parse JSON object from line: {line}. Error: {e}", flush=True)
    print(f"  Loaded {len(submitted_models)} generated models.", flush=True)

    summary_file_path = Path("summary.txt")
    top_level_temp_dir = tempfile.mkdtemp(prefix="cp_bench_eval_")

    try:
        start_time = time.time()
        evaluate_submission(submitted_models, summary_file_path, modelling_framework, top_level_temp_dir, dataset_file)
        elapsed_time = time.time() - start_time
    except Exception as e:
        click.echo(f"Error during evaluation: {e}")
        return

    click.echo("Evaluation complete!")
    click.echo(f"Results written to {summary_file_path}")
    click.echo(f"Total evaluation time: {elapsed_time:.2f} seconds")

    # Clean up temporary directory
    if os.path.exists(top_level_temp_dir):
        try:
            os.rmdir(top_level_temp_dir)
        except OSError as e:
            click.echo(f"Warning: Could not remove temporary directory {top_level_temp_dir}: {e}")
    else:
        click.echo(f"Temporary directory {top_level_temp_dir} does not exist, nothing to clean up.")


if __name__ == "__main__":
    main()
