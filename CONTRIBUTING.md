# Contributing to DCP-Bench-Open

We welcome contributions from the community to help this benchmark grow!

## How to Add a New Problem

The process for adding a new problem is straightforward. Please follow these steps:

1.  **Fork the repository**.
2.  **Add your problem** to the `dataset/` directory. Each problem requires a new subdirectory and two files within it:
    *   `<problem_name>/<problem_name>.cpmpy.py`: This file contains the constraint model written in CPMpy.
    *   `<problem_name>/<problem_name>.json`: This file contains the problem instances as a list of JSON objects.
3.  **Add the problem source** to `SOURCES.md` if it comes from a new source not already listed (this is optional but encouraged).
4.  **Run the self-consistency check** by executing the `self_consistency.py` script. This ensures that your files are correctly formatted and the provided example solution is valid.
5.  **Create a pull request** to the main repository with your changes.

### Python Model File (`<problem_name>/<problem_name>.cpmpy.py`)

Please follow the structure of existing problems. We use `dataset/csplib_054_n_queens/csplib_054_n_queens.cpmpy.py` as an example.

1.  **Metadata:** Include metadata and source links as comments at the top of the file.

    ```python
    # Category: csplib
    # Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob054_n_queens.py
    # Source description: https://www.csplib.org/Problems/prob054/
    ```

2.  **Problem Description:** Provide a clear, human-readable problem description within a docstring (`"""..."""`).
    *   The description should be easy to understand and avoid overly technical terms.
    *   It must end with a `Print` statement that specifies the decision variable(s) to be included in the solution output. This statement is crucial for evaluation. The variable names should be enclosed in parentheses, e.g., `(queens)`.

    ```python
    """
    Can \( n \) queens (of the same color) be placed on a \( n \times n \) chessboard so that none of the queens can attack
    each other? In chess, a queen attacks other squares on the same row, column or either diagonal as itself. So the
    \( n \-queens problem is to find a set of \( n \) locations on a chessboard, no two of which are on the same row,
    column or diagonal.

    Print the positions of the queens on the chessboard (queens) as a list of n integers - ranging from 1 to n, where the i-th
    integer represents the column position of the queen in the i-th row.
    """
    ```

3.  **Default Instance Data:** Include a default data instance between `# Data` and `# End of data` comments.
    *   This instance should ideally be simple and quickly solvable.
    *   This default instance **must** be the first entry in the corresponding `.json` file.
    *   If your problem has no parameters, you can skip this section and use an empty list (`[]`) in the `.json` file (see `dataset/abbots_puzzle/abbots_puzzle.cpmpy.py` for an example).

    ```python
    # Data
    n = 10  # Size of the chessboard and number of queens
    # End of data
    ```

4.  **CPMpy Model and Solution Output:**
    *   Implement the constraint model using the CPMpy library.
    *   The script must end by solving the model and printing the solution as a single-line JSON object. The keys of the JSON object should be the decision variables specified in the description's `Print` statement.

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
