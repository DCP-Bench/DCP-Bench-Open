import json
from ortools.sat.python import cp_model

# ------------------------------
# Input section (immutable)
# ------------------------------
# Nothing to parse in this specific instance because the numerical data
# are fixed in the requirements.  The placeholder is here in case future
# extensions supply data via standard input.

# ------------------------------
# Model creation
# ------------------------------
model = cp_model.CpModel()

# Parameters (constants)
h_small = 3   # lathe hours per small set
h_large = 2   # lathe hours per large set
lathe_capacity = 160  # total lathe hours available per week

w_small = 1   # kg boxwood per small set
w_large = 3   # kg boxwood per large set
wood_capacity = 200  # total kg of boxwood available per week

profit_small = 5   # $ profit per small set
profit_large = 20  # $ profit per large set

# ------------------------------
# Decision variables
# ------------------------------
# Upper bounds can be safely set to the maximum possible if only one
# resource were binding.  This keeps the search space tight.
max_small_by_lathe = lathe_capacity // h_small         # 160 // 3 ≈ 53
max_small_by_wood = wood_capacity // w_small           # 200
upper_bound_small = min(max_small_by_lathe, max_small_by_wood)

max_large_by_lathe = lathe_capacity // h_large         # 160 // 2 = 80
max_large_by_wood = wood_capacity // w_large           # 200 // 3 ≈ 66
upper_bound_large = min(max_large_by_lathe, max_large_by_wood)

small_set = model.NewIntVar(0, upper_bound_small, "small_set")
large_set = model.NewIntVar(0, upper_bound_large, "large_set")

# Total profit can be derived, but defining it as a separate variable can
# make extraction cleaner.
max_profit = model.NewIntVar(0, profit_small * upper_bound_small +
                                profit_large * upper_bound_large,
                             "max_profit")

# ------------------------------
# Constraints
# ------------------------------
# 1. Lathe capacity
model.Add(h_small * small_set + h_large * large_set <= lathe_capacity)

# 2. Boxwood availability
model.Add(w_small * small_set + w_large * large_set <= wood_capacity)

# 3. Profit definition
model.Add(max_profit == profit_small * small_set + profit_large * large_set)

# ------------------------------
# Objective: maximise profit
# ------------------------------
model.Maximize(max_profit)

# ------------------------------
# Solve model
# ------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ------------------------------
# Output results in required JSON format
# ------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        "large_set": solver.Value(large_set),
        "small_set": solver.Value(small_set),
        "max_profit": solver.Value(max_profit)
    }
else:
    # If no feasible solution was found, adhere to key structure with None values
    result = {
        "large_set": None,
        "small_set": None,
        "max_profit": None
    }

print(json.dumps(result))