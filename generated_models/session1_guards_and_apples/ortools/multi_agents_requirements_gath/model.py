import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Apple-gate puzzle solved with Google OR-Tools CP-SAT
# --------------------------------------------------
# A boy passes 5 gates; at each gate he pays half his apples plus one.
# After the last gate he keeps exactly one apple for the girl.
# The task is to find the apple counts immediately before each gate
# and directly after the last gate.
# --------------------------------------------------

def main():
    # -------------------------
    # 1. Create the CP-SAT model
    # -------------------------
    model = cp_model.CpModel()

    G = 5                     # number of gates
    MAX_A = 10 ** 6           # generous upper bound for apples

    # Decision variables: apples_before_gate_1 .. apples_before_gate_5, apples_after_gate_5
    apples = [model.NewIntVar(0, MAX_A, f"apples_{i+1}") for i in range(G + 1)]

    # -------------------------
    # 2. Add constraints
    # -------------------------
    # Final apple for the girl
    model.Add(apples[-1] == 1)      # A_6 = 1

    # Gate transfer constraints
    # Derived equality:      2 * A_{i+1} = A_i - 2      (i = 1..5)
    for i in range(G):
        model.Add(apples[i] - 2 * apples[i + 1] == 2)

    # -------------------------
    # 3. Solve (pure feasibility)
    # -------------------------
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # -------------------------
    # 4. Output solution as JSON
    # -------------------------
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        solution = [solver.Value(a) for a in apples]
        print(json.dumps({"apples": solution}))
    else:
        # Theoretically unreachable for this puzzle, but kept for completeness
        print(json.dumps({"apples": []}))


if __name__ == "__main__":
    main()
