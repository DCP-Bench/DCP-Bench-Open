from ortools.sat.python import cp_model
import json

# Input data
l = 9  # Value of l (must be an odd positive integer)
m = (l - 1) // 2

# Model definition
model = cp_model.CpModel()

# Domains: variables take values in {-1, +1}
# We represent -1 as 0 and +1 as 1 internally, then map back when printing
# This is because CP-SAT works with non-negative integers
# We'll create variables with domain {0,1} and interpret 0 as -1, 1 as +1

# Decision Variables
a_vars = [model.NewIntVar(0, 1, f'a_{i+1}') for i in range(l)]
b_vars = [model.NewIntVar(0, 1, f'b_{i+1}') for i in range(l)]

# Helper function to convert variable value (0 or 1) to -1 or +1
def val_to_pm1(val):
    return 2 * val - 1  # 0 -> -1, 1 -> +1

# Constraints

# Quadratic constraints:
# For s in 1..m:
# sum_{i=1}^l a_i * a_{(i+s) mod l} + b_i * b_{(i+s) mod l} = -2
# Since a_i and b_i are in {-1, +1}, product is also in {-1, +1}
# We model product as a new variable with domain {-1, +1} represented as {0,1}
# product = a_i * a_j
# product in {-1, +1} mapped to {0,1} as above
# product = 1 if a_i == a_j else -1
# So product = 1 if a_i == a_j else -1
# So product_var = 1 if a_i == a_j else 0 (in 0/1 domain)
# But we want product in {-1, +1} mapped to {0,1}
# So product_var = 1 if equal else 0
# Then sum of products in {-1,+1} domain is sum of (2*product_var -1)
# sum_{i} product = sum_i (2*product_var_i -1) = 2*sum_i product_var_i - l
# So sum_i product_var_i = (sum_i product + l)/2

# The constraint:
# sum_i (a_i * a_{i+s}) + sum_i (b_i * b_{i+s}) = -2
# In terms of product_vars:
# 2 * sum_i product_a_vars - l + 2 * sum_i product_b_vars - l = -2
# 2 * (sum_i product_a_vars + sum_i product_b_vars) - 2*l = -2
# 2 * (sum_i product_a_vars + sum_i product_b_vars) = 2*l - 2
# sum_i product_a_vars + sum_i product_b_vars = l - 1

# So for each s, sum of product_a_vars + sum of product_b_vars = l - 1

for s in range(1, m + 1):
    product_a_vars = []
    product_b_vars = []
    for i in range(l):
        j = (i + s) % l
        # product_a_var = 1 if a_i == a_j else 0
        eq_a = model.NewBoolVar(f'eq_a_{i+1}_{j+1}_s{s}')
        model.Add(a_vars[i] == a_vars[j]).OnlyEnforceIf(eq_a)
        model.Add(a_vars[i] != a_vars[j]).OnlyEnforceIf(eq_a.Not())
        product_a_vars.append(eq_a)

        # product_b_var = 1 if b_i == b_j else 0
        eq_b = model.NewBoolVar(f'eq_b_{i+1}_{j+1}_s{s}')
        model.Add(b_vars[i] == b_vars[j]).OnlyEnforceIf(eq_b)
        model.Add(b_vars[i] != b_vars[j]).OnlyEnforceIf(eq_b.Not())
        product_b_vars.append(eq_b)

    model.Add(sum(product_a_vars) + sum(product_b_vars) == l - 1)

# Linear constraints:
# sum of a_i = 1 in {-1,+1} domain
# sum_i a_i = 1
# sum_i (2*a_vars[i] - 1) = 1
# 2*sum_i a_vars[i] - l = 1
# 2*sum_i a_vars[i] = l + 1
# sum_i a_vars[i] = (l + 1)/2

model.Add(sum(a_vars) == (l + 1) // 2)
model.Add(sum(b_vars) == (l + 1) // 2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    a = [val_to_pm1(solver.Value(var)) for var in a_vars]
    b = [val_to_pm1(solver.Value(var)) for var in b_vars]
    solution = {
        'a': a,
        'b': b
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")