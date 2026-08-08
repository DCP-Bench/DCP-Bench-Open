from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Variables: my age (m) and husband's age (h)
# Assuming reasonable age bounds for adults
m = model.NewIntVar(1, 120, 'm')
h = model.NewIntVar(1, 120, 'h')

# The four operations to apply in some order:
# +2, /8, -3, *7
# We apply these four operations in some order to m to get h
# and apply the same four operations in a different order to h to get m

# We need to represent the order of operations for both sequences
# There are 4 operations, so 4! = 24 possible orders
# We'll represent the order as a permutation of indices [0,1,2,3]
# where 0: +2, 1: /8, 2: -3, 3: *7

# Create variables for the order of operations for m->h and h->m
order_mh = [model.NewIntVar(0, 3, f'order_mh_{i}') for i in range(4)]
order_hm = [model.NewIntVar(0, 3, f'order_hm_{i}') for i in range(4)]

# AllDifferent constraints for the orders (permutations)
model.AddAllDifferent(order_mh)
model.AddAllDifferent(order_hm)

# The operations as functions:
# We'll apply operations step by step, so create intermediate variables for each step
# For m->h:
step_mh = [model.NewIntVar(-10000, 10000, f'step_mh_{i}') for i in range(5)]
# step_mh[0] = m (start)
model.Add(step_mh[0] == m)

# For h->m:
step_hm = [model.NewIntVar(-10000, 10000, f'step_hm_{i}') for i in range(5)]
# step_hm[0] = h (start)
model.Add(step_hm[0] == h)

# Define the operations as functions on variables:
# Because division by 8 must be exact (integer division), we enforce that step is divisible by 8
# We'll implement the operations as constraints depending on the operation index

def apply_operation(model, prev, op_idx, result):
    # op_idx is an IntVar in [0..3]
    # prev and result are IntVars
    # We create intermediate boolean variables for each operation to select which op is applied
    is_add2 = model.NewBoolVar('')
    is_div8 = model.NewBoolVar('')
    is_sub3 = model.NewBoolVar('')
    is_mul7 = model.NewBoolVar('')

    model.Add(op_idx == 0).OnlyEnforceIf(is_add2)
    model.Add(op_idx != 0).OnlyEnforceIf(is_add2.Not())

    model.Add(op_idx == 1).OnlyEnforceIf(is_div8)
    model.Add(op_idx != 1).OnlyEnforceIf(is_div8.Not())

    model.Add(op_idx == 2).OnlyEnforceIf(is_sub3)
    model.Add(op_idx != 2).OnlyEnforceIf(is_sub3.Not())

    model.Add(op_idx == 3).OnlyEnforceIf(is_mul7)
    model.Add(op_idx != 3).OnlyEnforceIf(is_mul7.Not())

    # result = prev + 2 if is_add2
    model.Add(result == prev + 2).OnlyEnforceIf(is_add2)

    # result = prev / 8 if is_div8, and prev divisible by 8
    # To enforce divisibility, create an auxiliary variable q: prev = 8 * q
    q = model.NewIntVar(-10000, 10000, '')
    model.AddMultiplicationEquality(prev, [q, 8]).OnlyEnforceIf(is_div8)
    model.Add(result == q).OnlyEnforceIf(is_div8)

    # result = prev - 3 if is_sub3
    model.Add(result == prev - 3).OnlyEnforceIf(is_sub3)

    # result = prev * 7 if is_mul7
    model.AddMultiplicationEquality(result, [prev, 7]).OnlyEnforceIf(is_mul7)

# Apply operations for m->h
for i in range(4):
    apply_operation(model, step_mh[i], order_mh[i], step_mh[i+1])

# The final result after 4 operations starting from m is h
model.Add(step_mh[4] == h)

# Apply operations for h->m
for i in range(4):
    apply_operation(model, step_hm[i], order_hm[i], step_hm[i+1])

# The final result after 4 operations starting from h is m
model.Add(step_hm[4] == m)

# The order of operations for m->h and h->m must be different
# So at least one position differs
diff = []
for i in range(4):
    b = model.NewBoolVar('')
    model.Add(order_mh[i] != order_hm[i]).OnlyEnforceIf(b)
    model.Add(order_mh[i] == order_hm[i]).OnlyEnforceIf(b.Not())
    diff.append(b)
model.AddBoolOr(diff)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'm': solver.Value(m),
        'h': solver.Value(h)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")