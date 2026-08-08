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

# Model definition
model = cp_model.CpModel()

n = len(movies)

# Decision variables: 1 if movie i is selected, 0 otherwise
selected_movies = [model.NewBoolVar(f'selected_{i}') for i in range(n)]

# Constraints: no two selected movies can overlap
for i in range(n):
    for j in range(i + 1, n):
        start_i, end_i = movies[i][1], movies[i][2]
        start_j, end_j = movies[j][1], movies[j][2]
        # Check if intervals overlap
        # Overlap if start_i <= end_j and start_j <= end_i
        if not (end_i < start_j or end_j < start_i):
            # If they overlap, both cannot be selected simultaneously
            model.AddBoolOr([selected_movies[i].Not(), selected_movies[j].Not()])

# Objective: maximize the number of selected movies
model.Maximize(sum(selected_movies))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    selected = [solver.Value(var) for var in selected_movies]
    solution = {
        'num_selected_movies': sum(selected),
        'selected_movies': selected
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")