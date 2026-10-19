# Toy problems

One program per problem directory, taking the instance JSON path as its only argument.

## Output convention (test only)

- One program per problem, named after the problem directory with its hyphens kept (`models/n-queens-all.py`); a compiled language builds first and runs the binary.
- The model is run with the instance JSON path as its only argument.
- Each solution is printed as one JSON object on one line on stdout. Lines not starting with `{` are ignored.
- An infeasible instance prints exactly `{"status": "unsatisfiable"}`.
- Optimisation problems print exactly one solution, and it must be optimal; `knapsack-all-optimal` prints every optimal solution, each once.
