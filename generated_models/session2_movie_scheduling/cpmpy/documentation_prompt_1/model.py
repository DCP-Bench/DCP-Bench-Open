
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
n = len(movies)
starts = [m[1] for m in movies]
ends = [m[2] for m in movies]

# Model definition
model = cp.Model()

# Decision Variables
selected = cp.boolvar(shape=n, name="selected")

# Constraints
# No two selected movies can overlap
for i in range(n):
    for j in range(i+1, n):
        # If both selected, intervals must not overlap
        # Overlap condition: not (end_i < start_j or end_j < start_i)
        # So, if both selected, then (ends[i] < starts[j]) or (ends[j] < starts[i])
        model += (selected[i] + selected[j] <= 1) | (ends[i] < starts[j]) | (ends[j] < starts[i])

# Objective: maximize number of selected movies
model.maximize(cp.sum(selected))

# Solve and print
if model.solve():
    num_selected_movies = int(cp.sum(selected).value())
    selected_movies = selected.value().tolist()
    solution = {'num_selected_movies': num_selected_movies, 'selected_movies': [int(x) for x in selected_movies]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
