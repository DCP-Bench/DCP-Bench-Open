import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Problem constants (taken from the description)
# --------------------------------------------------
N = 13              # total number of entrants
M_TOTAL = 4         # total males (coded 0)
F_TOTAL = 9         # total females (coded 1)

# The instantaneous constraint 3·F_k ≤ 7·M_k can be rewritten as
#            10·F_k ≤ 7·k  →  F_k ≤ ⌊7·k/10⌋
# so we pre-compute the right-hand side for every prefix length k.
prefix_female_upper = [ (7 * k) // 10 for k in range(N + 1) ]  # index 0..N

# --------------------------------------------------
# Build CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# Binary decision variables: sequence[t] == 1  ⇒  female enters at position t
sequence = [model.NewBoolVar(f'seq_{t}') for t in range(N)]

# 1. Cardinality constraints
model.Add(sum(sequence) == F_TOTAL)  # total females = 9
# (total males automatically enforced because N – females = 4)

# 2. First entrant must be male (0)
model.Add(sequence[0] == 0)

# 3. Prefix ratio constraints:  F_k ≤ ⌊7·k/10⌋  for every k = 1..N
for k in range(1, N + 1):
    # Linear expression for number of females in first k positions
    female_prefix = sum(sequence[:k])
    model.Add(female_prefix <= prefix_female_upper[k])

# --------------------------------------------------
# Solve (pure feasibility, no objective)
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError('No feasible sequence exists under given constraints.')

# --------------------------------------------------
# Extract and print solution as required JSON
# --------------------------------------------------
result_sequence = [int(solver.Value(var)) for var in sequence]
print(json.dumps({"sequence": result_sequence}))
