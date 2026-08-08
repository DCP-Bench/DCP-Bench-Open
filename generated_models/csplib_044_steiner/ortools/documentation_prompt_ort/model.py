from ortools.sat.python import cp_model
import json

# Input data
n = 9  # Order of the Steiner Triple System

# Number of triples required
num_triples = n * (n - 1) // 6

# Model definition
model = cp_model.CpModel()

# Decision Variables
# triples[t][e] = 1 if element e+1 is in triple t, else 0
triples = []
for t in range(num_triples):
    triple = [model.NewBoolVar(f't{t}_e{e}') for e in range(n)]
    triples.append(triple)

# Constraints

# Each triple has exactly 3 distinct elements
for t in range(num_triples):
    model.Add(sum(triples[t]) == 3)

# Each element appears in exactly (n-1)/2 triples
# This is a property of Steiner Triple Systems (BIBD parameters)
for e in range(n):
    model.Add(sum(triples[t][e] for t in range(num_triples)) == (n - 1) // 2)

# Any two triples have at most one common element
# For all pairs of triples t1 < t2, sum of common elements <= 1
for t1 in range(num_triples):
    for t2 in range(t1 + 1, num_triples):
        common_elements = []
        for e in range(n):
            # Create a bool var for common element presence in both triples
            common = model.NewBoolVar(f'common_t{t1}_t{t2}_e{e}')
            model.AddBoolAnd([triples[t1][e], triples[t2][e]]).OnlyEnforceIf(common)
            model.AddBoolOr([triples[t1][e].Not(), triples[t2][e].Not()]).OnlyEnforceIf(common.Not())
            common_elements.append(common)
        model.Add(sum(common_elements) <= 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract triples as sets of elements (1-based)
    solution_triples = []
    for t in range(num_triples):
        triple_set = []
        for e in range(n):
            if solver.Value(triples[t][e]) == 1:
                triple_set.append(e + 1)
        solution_triples.append(triple_set)
    solution = {'sets': solution_triples}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")