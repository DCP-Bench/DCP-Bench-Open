# Import libraries
from cpmpy import *
import json

# Parameters
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
n_movies = len(movies)

# Decision Variables
selected_movies = boolvar(shape=n_movies, name="selected_movies")  # Whether each movie is selected
num_selected_movies = intvar(0, n_movies, name="num_selected_movies")  # Number of selected movies

# Model
model = Model()

# Constraint: no overlapping movies can be selected
for i in range(n_movies):
    for j in range(i+1, n_movies):
        # Check if movies i and j overlap (precompute as Python bool)
        overlap = not (movies[i][2] < movies[j][1] or movies[j][2] < movies[i][1])
        if overlap:
            # If they overlap, at most one can be selected
            model += (selected_movies[i] + selected_movies[j]) <= 1

# Link selected_movies to num_selected_movies
model += num_selected_movies == sum(selected_movies)

# Objective: maximize number of selected movies
model.maximize(num_selected_movies)

# Solve
model.solve()

# Print solution with correct field order
solution = {
    "num_selected_movies": num_selected_movies.value(),
    "selected_movies": selected_movies.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script