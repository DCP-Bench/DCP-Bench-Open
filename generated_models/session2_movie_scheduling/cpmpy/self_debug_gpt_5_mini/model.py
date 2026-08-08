
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

# Model definition
model = cp.Model()

n = len(movies)

# Decision Variables: 1 if the movie is selected, 0 otherwise
selected = cp.boolvar(shape=n, name="selected")

# Constraints: no two overlapping intervals can both be selected
# Intervals [start, end] are considered inclusive; overlap if not (end_i < start_j or end_j < start_i)
for i in range(n):
    start_i = movies[i][1]
    end_i = movies[i][2]
    for j in range(i+1, n):
        start_j = movies[j][1]
        end_j = movies[j][2]
        # If intervals i and j overlap, they cannot both be selected
        if not (end_i < start_j or end_j < start_i):
            model += (selected[i] + selected[j] <= 1)

# Objective: maximize the number of selected movies (each pays the same)
model.maximize(cp.sum(selected))

# Solve and print
if model.solve():
    sel_list = selected.value().tolist()
    # convert booleans to 0/1 integers
    sel_ints = list(map(int, sel_list))
    solution = {'selected_movies': sel_ints}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
