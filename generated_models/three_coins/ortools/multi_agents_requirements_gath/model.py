import json
from ortools.sat.python import cp_model

# ------------------ Input data (immutable) ------------------
num_moves = 3                 # exact number of flips to perform
init = [1, 0, 1]              # 0 = heads, 1 = tails
num_coins = len(init)         # = 3

# ------------------ Model creation ------------------
model = cp_model.CpModel()

# Decision variables: steps[m] = index of coin flipped at move m
steps = [model.NewIntVar(0, num_coins - 1, f"step_{m}") for m in range(num_moves)]

# Auxiliary Booleans: flip[m][i] == 1  <=>  coin i is flipped at move m
flip = [[model.NewBoolVar(f"flip_{m}_{i}") for i in range(num_coins)]
        for m in range(num_moves)]

# 1) Exactly one coin is flipped in each move and link to steps[m]
for m in range(num_moves):
    # exactly one coin chosen
    model.Add(sum(flip[m][i] for i in range(num_coins)) == 1)
    # channeling flip[m][i] <-> (steps[m] == i)
    for i in range(num_coins):
        # If flip[m][i] is true  =>  steps[m] == i
        model.Add(steps[m] == i).OnlyEnforceIf(flip[m][i])
        # If flip[m][i] is false =>  steps[m] != i
        model.Add(steps[m] != i).OnlyEnforceIf(flip[m][i].Not())

# 2) Uniform final orientation constraint
z = model.NewBoolVar("common_face")  # 0=heads, 1=tails

for i in range(num_coins):
    total_flips_on_i = sum(flip[m][i] for m in range(num_moves))
    # init[i] + total_flips_on_i  must have the same parity as z
    # => init[i] + total_flips_on_i - z is even
    k = model.NewIntVar(-num_moves, num_moves, f"k_{i}")  # integer slack
    model.Add(init[i] + total_flips_on_i - z == 2 * k)

# ------------------ Solve ------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ------------------ Output ------------------
if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    result_steps = [int(solver.Value(var)) for var in steps]
    print(json.dumps({"steps": result_steps}))
else:
    # Should not happen for this tiny instance; still, stay compliant
    print(json.dumps({"steps": None}))
