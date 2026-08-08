from ortools.sat.python import cp_model
import json

# Input data
at_most = [1, 2, 2, 2, 1]  # max times a property can be present in per_slots window
per_slots = [2, 3, 3, 5, 5]  # size of the sliding window for each property
demand = [1, 1, 2, 2, 2, 2]  # demand per car type
requires = [
    [1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 0],
    [1, 1, 0, 0, 0]
]  # properties per car type

# Number of cars to produce
num_cars = sum(demand)
num_types = len(demand)
num_props = len(at_most)

# Model definition
model = cp_model.CpModel()

# Decision variables
# sequence[i] = car type at position i in the sequence
sequence = [model.NewIntVar(0, num_types - 1, f'seq_{i}') for i in range(num_cars)]

# Constraints

# 1) Demand constraints: each car type appears exactly demand[type] times
for t in range(num_types):
    model.Add(sum(sequence[i] == t for i in range(num_cars)) == demand[t])

# 2) Capacity constraints for each property:
# For each property p, in every window of size per_slots[p], the number of cars
# requiring that property is at most at_most[p].
for p in range(num_props):
    window_size = per_slots[p]
    max_allowed = at_most[p]
    for start in range(num_cars - window_size + 1):
        # Count how many cars in sequence[start:start+window_size] require property p
        # We create boolean variables for each position in the window indicating if that car requires property p
        bool_vars = []
        for pos in range(start, start + window_size):
            # Create boolean variables for each car type indicating if sequence[pos] == t
            # Then sum requires[t][p] * (sequence[pos] == t) over t
            # We can do this by creating intermediate bool variables for (sequence[pos] == t)
            # and then sum requires[t][p] * that bool var
            # But to avoid many bool vars, we use AddAllowedAssignments with a table
            # Instead, we create a bool var for "car at pos requires property p"
            b = model.NewBoolVar(f'pos{pos}_prop{p}')
            # Allowed car types for which requires[t][p] == 1
            allowed_types = [t for t in range(num_types) if requires[t][p] == 1]
            # If sequence[pos] in allowed_types then b=1 else b=0
            # We enforce: b == OR over (sequence[pos] == t for t in allowed_types)
            # Create bool vars for sequence[pos] == t
            eq_bools = []
            for t in allowed_types:
                eq_bool = model.NewBoolVar(f'pos{pos}_eq_{t}_prop{p}')
                model.Add(sequence[pos] == t).OnlyEnforceIf(eq_bool)
                model.Add(sequence[pos] != t).OnlyEnforceIf(eq_bool.Not())
                eq_bools.append(eq_bool)
            if eq_bools:
                model.AddBoolOr(eq_bools).OnlyEnforceIf(b)
                model.AddBoolAnd([eb.Not() for eb in eq_bools]).OnlyEnforceIf(b.Not())
            else:
                # No car type requires this property, so b=0 always
                model.Add(b == 0)
            bool_vars.append(b)
        model.Add(sum(bool_vars) <= max_allowed)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'sequence': [solver.Value(sequence[i]) for i in range(num_cars)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")