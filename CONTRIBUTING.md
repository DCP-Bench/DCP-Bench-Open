# Contributing to DCP-Bench-Open

We welcome contributions from the community to help this benchmark grow!

## How to Add a New Problem

The process for adding a new problem is straightforward. Please follow these steps:

1.  **Fork the repository**.
2.  **Add your problem** to the `dataset/` directory. Each problem requires a new subdirectory and these files within it:
    *   `<problem_name>/description.md`: The natural language problem description, in Markdown.
    *   `<problem_name>/<problem_name>.cpmpy.py`: This file contains the constraint model written in CPMpy.
    *   `<problem_name>/<problem_name>.json`: This file contains the problem instances as a list of JSON objects.
    *   `<problem_name>/metadata.json`: The problem's facts for indexing and filtering. Generate it with `python -m dcp_bench.problems sync <problem_name>`.
3.  **Add the problem source** to `SOURCES.md` if it comes from a new source not already listed (this is optional but encouraged).
4.  **Run the self-consistency check** by executing the `self_consistency.py` script. This ensures that your files are correctly formatted and the provided example solution is valid.
5.  **Run the dataset audit**, which is what CI enforces:

    ```bash
    python -m unittest tests.test_dataset
    ```

    It checks that every problem has a description, that `metadata.json` is current, that every reference loads, that the first entry of the `.json` matches the embedded example exactly, that every listed instance builds the model, and that instances carry no extra keys beyond `name` and `note`.
6.  **Create a pull request** to the main repository with your changes.

### Problem Description (`<problem_name>/description.md`)

This is the text a model is written from, so it has to be complete without the reference. It can be as long as the problem needs, with sections, lists and tables.

*   The description should be easy to understand and avoid overly technical terms.
*   Write Markdown: put diagrams, grids and aligned tables of data in a fenced code block (` ```text `), or their layout is lost when rendered. Formulas go in `\( ... \)` or `$ ... $`.
*   It must end with a `Print` statement that specifies the decision variable(s) to be included in the solution output. This statement is crucial for evaluation. The variable names should be enclosed in parentheses, e.g., `(queens)`.

```markdown
Can \( n \) queens (of the same color) be placed on a \( n \times n \) chessboard so that none of the queens can attack
each other? In chess, a queen attacks other squares on the same row, column or either diagonal as itself. So the
\( n \)-queens problem is to find a set of \( n \) locations on a chessboard, no two of which are on the same row,
column or diagonal.

Print the positions of the queens on the chessboard (queens) as a list of n integers - ranging from 1 to n, where the i-th
integer represents the column position of the queen in the i-th row.
```

### Metadata (`<problem_name>/metadata.json`)

Generated from the reference by `python -m dcp_bench.problems sync <problem_name>`; rerun it whenever the origin comments, the objective, the declared outputs or the data section change. It holds `id`, `category`, `sources` (each with a `kind` of `origin`, `description`, `model`, `instances` or `note`, and a `url` or `text`), `objective` (`satisfaction`, `minimize` or `maximize`), `outputs`, `instance_fields`, and optionally `name` and `timeout`. A key you add by hand, such as a tag, is kept across syncs.

Use it to select problems, for example `python -m dcp_bench.problems list --category csplib --objective minimize`.

### Python Model File (`<problem_name>/<problem_name>.cpmpy.py`)

Please follow the structure of existing problems. We use `dataset/csplib_054_n_queens/csplib_054_n_queens.cpmpy.py` as an example.

1.  **Origin:** Include the category and source links as `# Key: value` comments at the top of the file, followed by a blank line. `metadata.json` is generated from them. The keys are `Category`, `Source`, `Source description`, `Source model`, `Problem instances`, `Misc`, `Name` and `Timeout`, and a source may be a URL or a citation.

    ```python
    # Category: csplib
    # Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob054_n_queens.py
    # Source description: https://www.csplib.org/Problems/prob054/
    ```

2.  **Default Instance Data:** Include a default data instance between `# Data` and `# End of data` comments.
    *   This instance should ideally be simple and quickly solvable.
    *   This default instance **must** be the first entry in the corresponding `.json` file.
    *   If your problem has no parameters, you can skip this section and use an empty list (`[]`) in the `.json` file (see `dataset/abbots_puzzle/abbots_puzzle.cpmpy.py` for an example).

    ```python
    # Data
    n = 10  # Size of the chessboard and number of queens
    # End of data
    ```

3.  **CPMpy Model and Solution Output:**
    *   Implement the constraint model using the CPMpy library.
    *   The script must end by solving the model and printing the solution as a single-line JSON object. The keys of the JSON object should be the decision variables specified in the `Print` statement of `description.md`.

    ```python
    # (CPMpy model implementation)
    ...
    model.solve()

    # Print the solution in JSON format
    solution = {"queens": queens.value().tolist()}
    print(json.dumps(solution))
    ```

### JSON Instance File (`<problem_name>/<problem_name>.json`)

*   This file should contain a list of JSON objects.
*   Each object represents one instance of the problem, with keys corresponding to the parameters used in the Python model.
*   Remember, the first instance in this file must match the default instance in the `.py` file.
*   Besides those parameters, only `name` and `note` are allowed as extra keys.
*   Every instance must be satisfiable (for now).
*   To add instances to an existing problem, put the candidates in a separate JSON list, each with a `note` saying where it comes from, and run `python -m generation.instances check PROBLEM candidates.json --append` from a [DCP Rosetta](https://github.com/DCP-Bench/DCP-Rosetta) checkout, where this repository is the `bench/` submodule. It checks the fields and their shapes, that the instance is new, and that the reference solves it (or proves its optimum) within 10 seconds, then appends the ones that pass. DCP Rosetta's `skills/instance-curator` has the full procedure, including rechecking the models already generated for the problem.

Example for `csplib_054_n_queens.json`:
```json
[
  {
    "n": 10
  },
  {
    "n": 11
  },
  {
    "n": 12
  }
]
```

Thank you for helping us improve this repository!
