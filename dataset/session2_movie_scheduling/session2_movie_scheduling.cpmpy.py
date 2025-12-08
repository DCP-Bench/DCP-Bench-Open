#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/movie_scheduling.mzn
# Source description: Steven S. Skiena's The Algorithm Design Manual

"""
Consider the following scheduling problem. Imagine you are a highly-in-
demand actor, who has been presented with offers to star in n different movie
projects under development. Each offer comes specified with the first and last day
of filming. To take the job, you must commit to being available throughout this
entire period. Thus, you cannot simultaneously accept two jobs whose intervals
overlap.
For an artist such as yourself, the criteria for job acceptance is clear: you want
to make as much money as possible. Because each of these films pays the same fee
per film, this implies you seek the largest possible set of jobs (intervals) such that
no two of them conflict with each other.

Input is a list of movies along with their first and last day of filming

Print which movies are accepted (selected_movies) as a list of booleans, where 1 indicates that the movie is selected
and 0 indicates that it is not selected-in the order of the input list.
"""

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
                and movies[i][2] > movies[j][1]  # Movie i ends after movie j starts
                and movies[j][2] > movies[i][1]  # Movie j ends after movie i starts
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
