
import cpmpy as cp
import json

movies = [
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

selected = cp.boolvar(shape=n, name="selected")
model = cp.Model()

for i in range(n):
    for j in range(i + 1, n):
        s_i, e_i = starts[i], ends[i]
        s_j, e_j = starts[j], ends[j]
        if (s_i < e_j) and (s_j < e_i):
            model += (selected[i] + selected[j] <= 1)

model.maximize(cp.sum(selected))

if model.solve():
    solution = {
        'num_selected_movies': int(model.objective_value()),
        'selected_movies': selected.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
