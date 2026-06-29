#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/tsp.py
# Description: https://en.wikipedia.org/wiki/Travelling_salesman_problem

"""
The travelling salesman problem, also known as the travelling salesperson problem (TSP), asks the following
question: "Given a list of cities and the distances between each pair of cities (or the locations of the cities), what
is the shortest possible route that visits each city exactly once and returns to the origin city?

Print the optimal travel distance (travel_distance) for the given locations; the distance is defined as the Euclidean
distance between the points rounded to an integer.
"""

# Data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]
# End of data

# Import libraries
import math
import numpy as np
from cpmpy import *
import json


# Parameters
def compute_euclidean_distance_matrix(locations):
    """Computes distances between all points (from ortools docs)."""
    n_city = len(locations)
    distances = np.zeros((n_city, n_city))
    for from_counter, from_node in enumerate(locations):
        for to_counter, to_node in enumerate(locations):
            if from_counter != to_counter:
                distances[from_counter][to_counter] = (
                    int(round(math.hypot((from_node[0] - to_node[0]),(from_node[1] - to_node[1])))))
    return distances.astype(int)


distance_matrix = compute_euclidean_distance_matrix(locations)
n_city = len(locations)

# we use the successor variable formulation and circuit global constraint here
# alternative is to model like in vrp.py

# x[i]=j means that j is visited immediately after i
x = intvar(0, n_city - 1, shape=n_city)

# The 'circuit' global constraint ensures that the successor variables from a circuit
model = Model(Circuit(x))

# the objective is to minimize the travelled distance
distance_matrix = cpm_array(distance_matrix)  # for indexing with variable
travel_distance = sum(distance_matrix[i, x[i]] for i in range(n_city))
model.minimize(travel_distance)

# Solve
model.solve()

# Print
solution = {"travel_distance": int(travel_distance.value())}
print(json.dumps(solution))
