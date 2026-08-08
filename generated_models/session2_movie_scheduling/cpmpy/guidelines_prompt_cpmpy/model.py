
import cpmpy as cp
import json

# Data
movies = [  # title, start, end
    ["Tarjan of the Jungle", 4, 13],
    ["The Four Volume Problem", 17, 27],
    ["The President's Algorist", 1, 10],
    ["Steiner's Tree", 12, 18],
    ["Process Terminated", 23, 30],
    ["Halting State", 9, 16],
    ["Programming Challenges", 19, 25],
    ["Discrete Mathematics", 2, 7],
    ["Calculated Bets", 26, 31]
]
# End of data

# Extract start and end times
n = len(movies)
starts = [movies[i][1] for i in range(n)]
ends = [movies[i][2] for i in range(n)]

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if movie i is selected, 0 otherwise
x = cp.intvar(0, 1, shape=n, name="x")

# Constraints: no overlapping intervals
for i in range(n):
    for j in range(i + 1, n):
        # overlap if start_i <= end_j and start_j <= end_i
        if starts[i] <= ends[j] and starts[j] <= ends[i]:
            model += x[i] + x[j] <= 1

# Objective: maximize number of selected movies
model.maximize(cp.sum(x))

# Solve and print
if model.solve():
    selected = [int(v) for v in x.value().tolist()]
    solution = {
        "num_selected_movies": int(model.objective_value()),
        "selected_movies": selected
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
