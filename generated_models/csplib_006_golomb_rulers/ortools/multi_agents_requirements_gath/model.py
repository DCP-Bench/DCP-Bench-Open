import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# 1. Parse input data (exactly as provided)
# --------------------------------------------------
size = 10  # Number of marks on the Golomb ruler (immutable)

# --------------------------------------------------
# 2. Create the CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# A loose but safe upper bound for the overall length.
# The optimal length for 10 marks is known to be 55, so 100 is sufficient.
MAX_LENGTH = 100

# --------------------------------------------------
# 3. Decision variables
# --------------------------------------------------
marks = []  # positions of the marks (including the first one at 0)
for i in range(size):
    # A simple lower bound: with i+1 marks we need at least the sum 1+2+..+i.
    lower_bound = i * (i + 1) // 2
    marks.append(model.NewIntVar(lower_bound, MAX_LENGTH, f"mark_{i}"))

length = marks[-1]  # Total length is the position of the last mark

# --------------------------------------------------
# 4. Constraints
# --------------------------------------------------
# 4.1 Fixed first mark
model.Add(marks[0] == 0)

# 4.2 Strictly increasing coordinates
for i in range(size - 1):
    model.Add(marks[i + 1] > marks[i])

# 4.3 All pairwise distances must be different (Golomb property)
differences = []
for i in range(size - 1):
    for j in range(i + 1, size):
        diff = model.NewIntVar(1, MAX_LENGTH, f"d_{i}_{j}")
        # diff = marks[j] - marks[i]
        model.Add(diff == marks[j] - marks[i])
        differences.append(diff)

# Use AllDifferent if available; otherwise fall back to pairwise != constraints
if hasattr(model, "AddAllDifferent"):
    model.AddAllDifferent(differences)
else:
    for i in range(len(differences)):
        for j in range(i + 1, len(differences)):
            model.Add(differences[i] != differences[j])

# 4.4 Symmetry breaking: first gap smaller than last gap
model.Add(marks[1] - marks[0] < marks[-1] - marks[-2])

# --------------------------------------------------
# 5. Objective: minimise the total length
# --------------------------------------------------
model.Minimize(length)

# --------------------------------------------------
# 6. Solve the model
# --------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60.0  # time limit (seconds)
solver.parameters.num_search_workers = 8       # use all available cores

status = solver.Solve(model)

# --------------------------------------------------
# 7. Output the result in the required JSON format
# --------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    marks_solution = [solver.Value(m) for m in marks]
    length_solution = solver.Value(length)
else:
    marks_solution = []
    length_solution = None

print(json.dumps({
    "marks": marks_solution,
    "length": length_solution
}))
