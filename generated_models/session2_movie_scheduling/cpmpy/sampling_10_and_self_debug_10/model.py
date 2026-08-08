
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

# Decision Variables: selected[i] = 1 if movie i is selected, else 0
selected = cp.intvar(0, 1, shape=n, name="selected")

# Constraints
# No two selected movies overlap
for i in range(n):
    for j in range(i+1, n):
        # If both selected, intervals must not overlap
        # Overlap condition: not (end_i < start_j or end_j < start_i)
        # So, if selected[i] and selected[j], then intervals do not overlap:
        # selected[i] + selected[j] <= 1 or intervals do not overlap
        # We can write: selected[i] + selected[j] <= 1 or (ends[i] < starts[j] or ends[j] < starts[i])
        # Using implication:
        # If selected[i] == 1 and selected[j] == 1 then intervals do not overlap
        # So: selected[i] & selected[j] => (ends[i] < starts[j] or ends[j] < starts[i])
        # This is equivalent to:
        # selected[i] + selected[j] <= 1 or (ends[i] < starts[j] or ends[j] < starts[i])
        # We can write as:
        # selected[i] + selected[j] <= 1 or (ends[i] < starts[j]) or (ends[j] < starts[i])
        # Using boolean variables and implications:
        # We'll use the following constraint:
        # selected[i] + selected[j] <= 1 or (ends[i] < starts[j]) or (ends[j] < starts[i])
        # In CPMpy, we can write:
        # selected[i] + selected[j] <= 1 or (ends[i] < starts[j]) or (ends[j] < starts[i])
        # But CPMpy does not support direct or of inequalities, so we use implication:
        # selected[i] & selected[j] => (ends[i] < starts[j]) or (ends[j] < starts[i])
        # We can write as:
        # selected[i].implies(~selected[j] | (ends[i] < starts[j]) | (ends[j] < starts[i]))
        # But better to write:
        # selected[i] & selected[j] => (ends[i] < starts[j]) or (ends[j] < starts[i])
        # Using cp.Or and cp.And:
        # cp.And(selected[i], selected[j]).implies(cp.Or(ends[i] < starts[j], ends[j] < starts[i]))
        # But ends[i], starts[j] are constants, so we can precompute the boolean condition:
        # overlap = not (ends[i] < starts[j] or ends[j] < starts[i])
        # So if overlap, then selected[i] + selected[j] <= 1
        # So if intervals overlap, then both cannot be selected simultaneously.
        if not (ends[i] < starts[j] or ends[j] < starts[i]):
            model += (selected[i] + selected[j] <= 1)

# Objective: maximize number of selected movies
model.maximize(cp.sum(selected))

# Solve and print
if model.solve():
    num_selected_movies = int(cp.sum(selected).value())
    selected_movies = selected.value().tolist()
    solution = {'num_selected_movies': num_selected_movies, 'selected_movies': selected_movies}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
