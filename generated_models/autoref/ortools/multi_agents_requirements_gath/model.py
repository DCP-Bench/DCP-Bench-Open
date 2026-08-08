import json
import re
from ortools.sat.python import cp_model

# ------------------------------------------------------------
# 1. Parse the exact input data string (kept literal as given)
# ------------------------------------------------------------
input_data = """n = 27 m = 5"""

# Extract the two integers: n and m (order matters)
values = list(map(int, re.findall(r"-?\d+", input_data)))
if len(values) != 2:
    raise ValueError("Input string must contain exactly two integers: n and m.")

n, m = values  # n > 0, m >= 0

# ------------------------------------------------------------
# 2. Build the CP-SAT model
# ------------------------------------------------------------
model = cp_model.CpModel()

seq_len = n + 2                  # total positions in the sequence
upper   = max(seq_len, m)        # safe upper bound for any element of S

# Decision variables: sequence elements s[0] .. s[n+1]
s = [model.NewIntVar(0, upper, f"s[{j}]") for j in range(seq_len)]

# Tail value constraint: s[n+1] = m
model.Add(s[n + 1] == m)

# ------------------------------------------------------------
# 3. Indicator matrix  is_val[j][v]  ↔  (s[j] == v)
# ------------------------------------------------------------
# Each position chooses exactly one value from 0..upper.
# The linear channel guarantees consistency without using
# unsupported reified "!=" constraints.
is_val = []  # is_val[j][v]
for j in range(seq_len):
    row = [model.NewBoolVar(f"is_val[{j},{v}]") for v in range(upper + 1)]
    model.AddExactlyOne(row)                                      # one value per position
    model.Add(sum(v * row[v] for v in range(upper + 1)) == s[j])  # channel value to s[j]
    is_val.append(row)

# ------------------------------------------------------------
# 4. Self-count constraints:  s[i] = occurrences of value i
# ------------------------------------------------------------
for i in range(n + 1):
    occurrences_of_i = sum(is_val[j][i] for j in range(seq_len))
    model.Add(s[i] == occurrences_of_i)

# ------------------------------------------------------------
# 5. Solve (feasibility only)
# ------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 8      # parallel search
solver.parameters.max_time_in_seconds = 30.0  # safety guard

status = solver.Solve(model)

# ------------------------------------------------------------
# 6. Output in required JSON format
# ------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    sequence = [solver.Value(var) for var in s]
else:
    sequence = []  # infeasible or unknown

print(json.dumps({"s": sequence}))
