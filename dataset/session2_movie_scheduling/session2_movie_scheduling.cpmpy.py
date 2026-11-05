#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/movie_scheduling.mzn
# Source description: Steven S. Skiena's The Algorithm Design Manual

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

# Import libraries
from cpmpy import *
import json

# Parameters
num_movies = len(movies)

# Decision Variables
selected_movies = boolvar(shape=num_movies, name="selected_movies")  # 1 if the movie is selected, 0 otherwise
num_selected_movies = sum(selected_movies)  # Number of selected movies

# Model
model = Model()

# Add constraint for non-overlapping movie schedules
for i in range(num_movies):
    for j in range(num_movies):
        # Check if the intervals overlap for each pair of movies
        if (i != j  # Different movies
                and movies[i][2] >= movies[j][1]  # Movie i ends on or after the day movie j starts
                and movies[j][2] >= movies[i][1]  # Movie j ends on or after the day movie i starts
        ):
            # Then, the movies cannot be selected together
            model += selected_movies[i] + selected_movies[j] <= 1

# Objective: Maximize the number of selected movies
model.maximize(num_selected_movies)

# Solve
model.solve()

# Print
solution = {"selected_movies": selected_movies.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
