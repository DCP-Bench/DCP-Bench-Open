
from ortools.sat.python import cp_model
import json

# Input data
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

# Number of movies
n = len(movies)

# Model definition
model = cp_model.CpModel()

# Decision Variables: select movie i or not
selected = [model.NewBoolVar(f"selected_{i}") for i in range(n)]

# Constraints: no two overlapping movies can both be selected
for i in range(n):
    start_i, end_i = movies[i][1], movies[i][2]
    for j in range(i + 1, n):
        start_j, end_j = movies[j][1], movies[j][2]
        # If intervals overlap (inclusive), they cannot both be selected
        if not (end_i < start_j or end_j < start_i):
            model.Add(selected[i] + selected[j] <= 1)

# Objective: maximize the number of selected movies
model.Maximize(sum(selected))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    sol_selected = [solver.Value(var) for var in selected]
    solution = {
        "num_selected_movies": int(solver.ObjectiveValue()),
        "selected_movies": sol_selected
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
