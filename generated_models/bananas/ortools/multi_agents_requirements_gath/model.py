# complete, runnable Python program solving the fruit-purchase puzzle using Google OR-Tools
from ortools.sat.python import cp_model
import json

# ----------------------------
# Model construction
# ----------------------------
model = cp_model.CpModel()

# Bundle parameters (size and cost per bundle)
BUNDLE_SIZE = {
    'bananas': 5,
    'oranges': 7,
    'mangoes': 9,
    'apples': 3,
}
BUNDLE_COST = {
    'bananas': 3,
    'oranges': 5,
    'mangoes': 7,
    'apples': 9,
}
TOTAL_FRUITS = 100
BUDGET = 100

# Decision variables – number of bundles purchased (must be at least one of each)
max_bundles = {fruit: TOTAL_FRUITS // size for fruit, size in BUNDLE_SIZE.items()}
y = {
    fruit: model.NewIntVar(1, max_bundles[fruit], f'y_{fruit}') for fruit in BUNDLE_SIZE
}

# Constraint: total number of fruits
model.Add(
    sum(BUNDLE_SIZE[f] * y[f] for f in BUNDLE_SIZE) == TOTAL_FRUITS
)

# Constraint: total cost matches budget
model.Add(
    sum(BUNDLE_COST[f] * y[f] for f in BUNDLE_COST) == BUDGET
)

# Objective: minimise disliked fruits (bananas + apples counted in individual pieces)
disliked = model.NewIntVar(0, TOTAL_FRUITS, 'disliked')
model.Add(disliked == BUNDLE_SIZE['bananas'] * y['bananas'] + BUNDLE_SIZE['apples'] * y['apples'])
model.Minimize(disliked)

# ----------------------------
# Solve model
# ----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # small instance; keep default search otherwise
status = solver.Solve(model)

# ----------------------------
# Extract and print solution
# ----------------------------
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError('No feasible solution found')

result = {
    'oranges': BUNDLE_SIZE['oranges'] * solver.Value(y['oranges']),
    'bananas': BUNDLE_SIZE['bananas'] * solver.Value(y['bananas']),
    'apples':  BUNDLE_SIZE['apples']  * solver.Value(y['apples']),
    'mangoes': BUNDLE_SIZE['mangoes'] * solver.Value(y['mangoes']),
}

print(json.dumps(result))
