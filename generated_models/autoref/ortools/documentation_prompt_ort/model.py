from ortools.sat.python import cp_model
import json

# Input data
n = 27
m = 5

# Model definition
model = cp_model.CpModel()

# Decision Variables
# s[i] = number of occurrences of i in S, for i in [0..n]
s = [model.NewIntVar(0, 1000, f's[{i}]') for i in range(n + 1)]

# s[n+1] = m (given)
# We will not include s[n+1] in s array, but we know s[n+1] = m
# The series S = (s0, s1, ..., sn, sn+1) with s[n+1] = m

# Constraints
# 1) For each i in [0..n], s[i] occurrences of i in S
# This means the count of i in S is s[i]
# The length of S is sum of all s[i] plus s[n+1] = m
# But s[n+1] = m is fixed

# 2) The series S must contain s[i] occurrences of i for i in [0..n]
# So the count of i in S is s[i]

# The series S is (s0, s1, ..., sn, sn+1)
# So the count of i in S is the number of times i appears in the series S
# But the series S is defined by the counts s[i], so the counts must be consistent:
# For each i in [0..n], s[i] = number of times i appears in S
# But S is the sequence of length n+2: (s0, s1, ..., sn, sn+1)
# So the count of i in S is the number of indices j in [0..n+1] such that s[j] = i
# Wait, this is a self-referential definition:
# s[i] = number of times i appears in S
# S = (s0, s1, ..., sn, sn+1)
# So s[i] = count of i in (s0, s1, ..., sn, m)

# So the problem is to find s0..sn such that for each i in [0..n]:
# s[i] = count of i in (s0, s1, ..., sn, m)
# and s[n+1] = m (given)

# So we have n+1 variables s[0..n]
# The series S is length n+2: s0..sn plus m at the end
# For each i in [0..n], s[i] = number of times i appears in S

# Let's define the counts of each value i in S:
# count_i = number of indices j in [0..n] with s[j] = i plus (1 if m == i else 0)

# So for each i in [0..n]:
# s[i] = count of i in s[0..n] + (1 if m == i else 0)

# We can model this with auxiliary boolean variables:
# For each i in [0..n], for each j in [0..n], define b[i][j] = 1 if s[j] == i else 0
# Then sum_j b[i][j] + (1 if m == i else 0) == s[i]

# Implementing this:

b = []
for i in range(n + 1):
    row = []
    for j in range(n + 1):
        # b[i][j] = 1 if s[j] == i else 0
        b_ij = model.NewBoolVar(f'b[{i}][{j}]')
        row.append(b_ij)
        # Link b_ij with s[j] == i
        model.Add(s[j] == i).OnlyEnforceIf(b_ij)
        model.Add(s[j] != i).OnlyEnforceIf(b_ij.Not())
    b.append(row)

for i in range(n + 1):
    # sum over j of b[i][j] + (1 if m == i else 0) == s[i]
    count_m = 1 if m == i else 0
    model.Add(s[i] == sum(b[i][j] for j in range(n + 1)) + count_m)

# The series S must be non-empty finite series
# Since s[n+1] = m is given, and m >= 0, and n > 0, the series length is n+2
# So length is fixed, no need to add length constraints

# To avoid trivial all zeros solution, ensure s is non-empty
# But s[n+1] = m is given, so series length is n+2, so non-empty guaranteed

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    s_values = [solver.Value(s[i]) for i in range(n + 1)]
    # Append s[n+1] = m
    s_values.append(m)
    solution = {'s': s_values}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")