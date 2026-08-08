# Complete, runnable code to build a 4×4 magic square with OR-Tools CP-SAT

from ortools.sat.python import cp_model
import json


def main():
    # -------------------------------
    # Problem constants
    # -------------------------------
    n = 4  # size of the square
    max_val = n * n  # 16
    magic_sum = n * (max_val + 1) // 2  # 34 for n = 4

    # -------------------------------
    # Model definition
    # -------------------------------
    model = cp_model.CpModel()

    # Decision variables: square[i][j] ∈ {1,…,16}
    square = [[model.NewIntVar(1, max_val, f"cell_{i}_{j}") for j in range(n)] for i in range(n)]

    # All-different over the whole grid
    model.AddAllDifferent([square[i][j] for i in range(n) for j in range(n)])

    # Row and column sum constraints
    for i in range(n):
        model.Add(sum(square[i][j] for j in range(n)) == magic_sum)  # row i
    for j in range(n):
        model.Add(sum(square[i][j] for i in range(n)) == magic_sum)  # column j

    # Main diagonal
    model.Add(sum(square[i][i] for i in range(n)) == magic_sum)

    # Secondary diagonal
    model.Add(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    # -------------------------------
    # Invoke solver
    # -------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10  # Reasonable time limit

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible magic square found")

    # Extract solution
    result_square = [[solver.Value(square[i][j]) for j in range(n)] for i in range(n)]

    # -------------------------------
    # Output as JSON
    # -------------------------------
    print(json.dumps({"square": result_square}))


if __name__ == "__main__":
    main()
