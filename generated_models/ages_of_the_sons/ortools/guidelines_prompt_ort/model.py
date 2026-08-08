
from ortools.sat.python import cp_model
import json

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables for the sons' ages (descending order)
A1 = model.NewIntVar(1, 36, 'A1')  # oldest
A2 = model.NewIntVar(1, 36, 'A2')
A3 = model.NewIntVar(1, 36, 'A3')

# Enforce non-increasing order: A1 >= A2 >= A3
model.Add(A1 >= A2)
model.Add(A2 >= A3)

# Product constraint: A1 * A2 * A3 == 36
# CP-SAT supports multiplication equality via AddMultiplicationEquality
t12 = model.NewIntVar(1, 36, 't12')
model.AddMultiplicationEquality(t12, [A1, A2])
prod = model.NewIntVar(1, 36, 'prod')
model.AddMultiplicationEquality(prod, [t12, A3])
model.Add(prod == 36)

# Callback to collect all solutions
class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, vars):
        super().__init__()
        self.vars = vars
        self.solutions = []  # list of tuples (A1, A2, A3)

    def OnSolutionCallback(self):
        sol = tuple(self.Value(v) for v in self.vars)
        self.solutions.append(sol)

# Solve and collect all valid triples
solver = cp_model.CpSolver()
collector = SolutionCollector([A1, A2, A3])
solver.SearchForAllSolutions(model, collector)

# Filter solutions by the puzzle logic:
# 1) Identify sums that occur more than once (ambiguous sum)
# 2) Among those, pick the one with a unique oldest son (A1 > A2)
all_sols = collector.solutions
# Compute sum frequencies
sum_counts = {}
for a, b, c in all_sols:
    s = a + b + c
    sum_counts[s] = sum_counts.get(s, 0) + 1

# Ambiguous sums: sums with more than one triple
ambiguous_sums = {s for s, cnt in sum_counts.items() if cnt > 1}

# Find the unique solution with ambiguous sum and unique oldest
final_sols = [
    (a, b, c)
    for (a, b, c) in all_sols
    if (a + b + c) in ambiguous_sums and a > b
]

# Prepare output
if final_sols:
    # There should be exactly one solution
    A1_val, A2_val, A3_val = final_sols[0]
    solution = {
        'A1': A1_val,
        'A2': A2_val,
        'A3': A3_val
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
