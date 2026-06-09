import os
import subprocess
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import tempfile
import re
import time


def remove_temp_file(path, retries=5, delay=0.1):
    for attempt in range(retries):
        try:
            os.remove(path)
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def run_instance(instance_path):
    """Run the instance file and capture the JSON output."""
    command = [sys.executable, instance_path]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {instance_path}: {result.stderr}")
        return None
    try:
        solution = json.loads(result.stdout)
        return solution
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {instance_path}")
        return None


def add_constraints_as_string(solution):
    """Generate constraints as a string to be added to the original script."""
    constraints = ""
    for key, value in solution.items():
        # Handle list values from json
        if isinstance(value, list):
            constraints += f"\nmodel += ({key} == {value})"
        else:
            constraints += f"\nmodel += ({key} == {value})"
    return constraints


def get_modified_script(script_content, solution):
    """Add constraints to the script content."""
    constraints_str = add_constraints_as_string(solution)
    modified_script = f"{script_content}\n{constraints_str}"
    modified_script += '''
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
'''
    return modified_script


def get_solutions(instance_path):
    """
    Run the instance file and capture the JSON output containing all solutions.
    This function will modify the script to use solveAll().
    """
    with open(instance_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    # Find the part of the script that solves the model and prints the solution
    solve_and_print_regex = re.compile(r"model\.solve\(.*", re.DOTALL)
    solve_and_print_block = solve_and_print_regex.search(script_content)

    if not solve_and_print_block:
        print(f"Could not find the solve and print block in {instance_path}")
        return None

    # Extract the solution dictionary string from the original script
    solution_dict_regex = re.compile(r"solution\s*=\s*{.*?}", re.DOTALL)
    match = solution_dict_regex.search(script_content)
    if not match:
        print(f"Could not find solution dictionary in {instance_path}")
        return None
    solution_dict_str = match.group(0)

    # Create the new code block for finding all solutions
    if 'nonogram' in instance_path or 'hidato' in instance_path:
        solver_part = ""
    elif 'resource_constrained_project_scheduling' in instance_path or 'candies' in instance_path:
        solver_part = ", solver='choco'"
    else:
        solver_part = ", solver='cpo'"

    new_code_block = f'''
# Solve the model
sols = []
def func():
    {solution_dict_str}
    sols.append(solution)

model.solveAll(display=func, solution_limit=2{solver_part})
import json
print(json.dumps(sols))
'''

    modified_script = script_content.replace(solve_and_print_block.group(0), new_code_block)

    # Create a temporary file to run the modified script
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as temp_file:
        temp_instance_path = temp_file.name
        temp_file.write(modified_script)

    command = [sys.executable, temp_instance_path]
    result = subprocess.run(command, capture_output=True, text=True)
    remove_temp_file(temp_instance_path)

    if result.returncode != 0:
        print(f"Error running modified script for {instance_path}: {result.stderr}")
        return None
    try:
        if not result.stdout.strip():
            return []
        solutions = json.loads(result.stdout)
        return solutions
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {instance_path}")
        print("Offending output:", result.stdout)
        return None


def check_consistency_for_solution(script_content, solution, instance_path):
    """Checks consistency for a single solution."""
    modified_script = get_modified_script(script_content, solution)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', dir=os.path.dirname(instance_path), encoding='utf-8') as temp_file:
        temp_instance_path = temp_file.name
        temp_file.write(modified_script)

    command = [sys.executable, temp_instance_path]
    result = subprocess.run(command, capture_output=True, text=True)
    remove_temp_file(temp_instance_path)

    if result.returncode != 0:
        print(f"Error running consistency check for {instance_path}: {result.stderr}")
        return False

    if 'ERROR' in result.stdout:
        return False

    return True


def check_consistency(instance_path, multi_solution_eval=False):
    print('Checking consistency for:', instance_path)

    if not multi_solution_eval:
        solution = run_instance(instance_path)
        if solution is None:
            return instance_path, False
        with open(instance_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
        return instance_path, check_consistency_for_solution(script_content, solution, instance_path)

    solutions = get_solutions(instance_path)

    if solutions is None or not solutions:
        return instance_path, False

    with open(instance_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    for solution in solutions:
        if not check_consistency_for_solution(script_content, solution, instance_path):
            print(f"Inconsistency found for solution: {solution} in file {instance_path} [FAIL]")
            return instance_path, False

    return instance_path, True


def main():
    # subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    dataset_folder = 'dataset'
    not_consistent = []
    instance_paths = []

    # Collect all instance file paths
    for root, dirs, files in os.walk(dataset_folder):
        for instance_file in files:
            if instance_file.endswith('.cpmpy.py'):
                instance_paths.append(os.path.join(root, instance_file))

    num_instances = len(instance_paths)
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(check_consistency, path, False): path for path in instance_paths}

        for future in as_completed(futures):
            try:
                instance_path, res = future.result()
                if not res:
                    not_consistent.append(instance_path)
                else:
                    print(f"Instance {instance_path} is self-consistent [OK]")
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")
                not_consistent.append(futures[future])

    print(f"\n{num_instances - len(not_consistent)}/{num_instances} instances are self-consistent.")
    if not_consistent:
        print("\nInstances that are not self-consistent:")
        for instance in not_consistent:
            print(f"- {instance}")
    else:
        print("All instances are self-consistent.")


def test_single_instance():
    """Tests the consistency check on a single file."""
    instance_path = "dataset/coin3_application/coin3_application.cpmpy.py"
    print(f"Testing instance: {instance_path}")
    instance_path_result, is_consistent = check_consistency(instance_path, multi_solution_eval=False)
    print(f"Instance {instance_path_result} is consistent: {is_consistent}")


if __name__ == '__main__':
    main()
    # test_single_instance()
