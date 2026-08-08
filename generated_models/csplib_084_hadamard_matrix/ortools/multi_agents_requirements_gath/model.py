import json
from ortools.sat.python import cp_model

# ----------------------------
# 1. Input data (immutable)
# ----------------------------
l = 9  # Value of l (must be an odd positive integer)
# ---------------------------------
# 2. Derived constants and helpers
# ---------------------------------
assert l % 2 == 1 and l > 0, "l must be a positive odd integer"
m = (l - 1) // 2  # number of quadratic constraints / shifts
indices = range(l)  # 0..l-1 for Python indexing

# ----------------------------
# 3. CP-SAT model definition
# ----------------------------
model = cp_model.CpModel()

# 3.1 Boolean representation for ±1 values
#        val = 2*bool - 1  →  {0,1}  ↦  {−1,+1}
# -----------------------------------------------------------------
a_bool = [model.NewBoolVar(f"a_bool_{i}") for i in indices]
b_bool = [model.NewBoolVar(f"b_bool_{i}") for i in indices]

# Create explicit IntVar "value" versions so they can participate in
# multiplication constraints.
a_val = [model.NewIntVar(-1, 1, f"a_{i}") for i in indices]
b_val = [model.NewIntVar(-1, 1, f"b_{i}") for i in indices]

for i in indices:
    # Link boolean indicator to ±1 value: a_val = 2*a_bool - 1
    model.Add(a_val[i] == a_bool[i] * 2 - 1)
    model.Add(b_val[i] == b_bool[i] * 2 - 1)

# 3.2 Linear sum constraints  Σ a_i = 1, Σ b_i = 1
model.Add(sum(a_val) == 1)
model.Add(sum(b_val) == 1)

# 3.3 Quadratic periodic autocorrelation constraints
for s in range(1, m + 1):
    # For every shift s, build the expression of paired products
    products_a = []
    products_b = []
    for i in indices:
        j = (i + s) % l  # periodic index
        # Product variables for a and b at this (i,s)
        prod_a = model.NewIntVar(-1, 1, f"prod_a_{i}_{s}")
        prod_b = model.NewIntVar(-1, 1, f"prod_b_{i}_{s}")

        # prod = val_i * val_j
        model.AddMultiplicationEquality(prod_a, [a_val[i], a_val[j]])
        model.AddMultiplicationEquality(prod_b, [b_val[i], b_val[j]])

        products_a.append(prod_a)
        products_b.append(prod_b)

    # Σ products_a + Σ products_b = -2
    model.Add(sum(products_a) + sum(products_b) == -2)

# ----------------------------
# 4. Solve the model (feasibility)
# ----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # small instance; safety cap
status = solver.Solve(model)

# ----------------------------
# 5. Extract and print solution
# ----------------------------
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    a_sequence = [int(solver.Value(a_val[i])) for i in indices]
    b_sequence = [int(solver.Value(b_val[i])) for i in indices]
    # Maintain key order as required: ['b', 'a']
    output = {
        "b": b_sequence,
        "a": a_sequence
    }
    print(json.dumps(output))
else:
    # Should not happen for the given input (instances are known to be solvable)
    raise RuntimeError("No solution found for the given l = %d" % l)
