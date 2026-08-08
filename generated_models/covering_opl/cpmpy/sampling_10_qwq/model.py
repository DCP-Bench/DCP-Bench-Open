
import cpmpy as cp
import json

# Data
nb_workers = 32
num_tasks = 15
Qualified = [
    [1, 9, 19, 22, 25, 28, 31],
    [2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32],
    [3, 10, 19, 24, 26, 30, 32],
    [4, 21, 25, 28, 32],
    [5, 11, 16, 22, 23, 27, 31],
    [6, 20, 24, 26, 30, 32],
    [7, 12, 17, 25, 30, 31],
    [8, 17, 20, 22, 23],
    [9, 13, 14, 26, 29, 30, 31],
    [10, 21, 25, 31, 32],
    [14, 15, 18, 23, 24, 27, 30, 32],
    [18, 19, 22, 24, 26, 29, 31],
    [11, 20, 25, 28, 30, 32],
    [16, 19, 23, 31],
    [9, 18, 26, 28, 31, 32]
]
Cost = [
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]

# Convert Qualified to 0-based indices
qualified_0based = []
for task_list in Qualified:
    qualified_0based.append([w - 1 for w in task_list])

model = cp.Model()

# Decision Variables
selected = cp.boolvar(shape=nb_workers, name="selected")

# Constraints: Each task must be covered by at least one worker
for task in range(num_tasks):
    workers_for_task = qualified_0based[task]
    model += cp.sum(selected[workers_for_task]) >= 1

# Objective: Minimize total cost
total_cost_expr = cp.sum(Cost[i] * selected[i] for i in range(nb_workers))
model.minimize(total_cost_expr)

# Solve and print
if model.solve():
    total_cost = int(model.objective_value())
    workers = selected.value().tolist()
    solution = {
        'total_cost': total_cost,
        'workers': workers
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
