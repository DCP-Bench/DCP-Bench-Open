
import cpmpy as cp
import json

# Data (optional)
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

# Model definition
model = cp.Model()

# Decision Variables
n = len(movies)
selected_movies = cp.boolvar(shape=n, name="selected_movies")

# Constraints
# No two selected intervals may overlap (inclusive intervals)
for i in range(n):
    si, ei = movies[i][1], movies[i][2]
    for j in range(i+1, n):
        sj, ej = movies[j][1], movies[j][2]
        # Overlap if intervals intersect: not (ei < sj or ej < si)
        overlap = not (ei < sj or ej < si)
        if overlap:
            model += (selected_movies[i] + selected_movies[j] <= 1)

# Objective (maximize the number of selected movies)
model.maximize(cp.sum(selected_movies))

# Solve and print
if model.solve():
    solution = {
        'selected_movies': list(map(int, selected_movies.value().tolist()))
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
