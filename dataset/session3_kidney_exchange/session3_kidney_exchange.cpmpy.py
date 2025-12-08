#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/kidney_exchange.mzn

"""
At the hospital n people are on a waiting list for a kidney’s transplant. We have the information about the
compatibility between these people as a directed graph: compatible[i] is the set of people to which i can donate.
Given this information, we want to maximize the number of people that receive a new kidney: anyone who gives a kidney
must receive one, and no person receives more than one kidney.

Print the transplants (transplants) as a list of lists, where transplants[i][j] is 1 if person i donates to person j,
and 0 otherwise.
"""

# Data
num_people = 8  # number of people
compatible = [  # 1-based indexing, compatible[i] is the list of people to which i can donate
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables
transplants = boolvar(shape=(num_people, num_people))  # transplants[i][j] is True if i donates to j

# Model setup
model = Model()

# Constraints for the transplant pairs
for i in range(num_people):
    # Anyone who gives a kidney must receive one
    gives_kidney = sum(transplants[i, :]) >= 1
    receives_kidney = sum(transplants[:, i]) >= 1
    model += gives_kidney.implies(receives_kidney)

    # Each person can donate to at most one person and receive from at most one person
    can_donate_once = sum(transplants[i, :]) <= 1
    can_receive_once = sum(transplants[:, i]) <= 1
    model += can_donate_once & can_receive_once

    # Compatibility constraint: if i can't donate to j, then transplants[i][j] must be 0 (adjust for 0-based indexing)
    model += [transplants[i, j] == 0 for j in range(num_people) if j + 1 not in compatible[i]]

# Objective: maximize the number of transplants
model.maximize(sum(transplants))

# Solve
model.solve()

# Print the solution
solution = {"transplants": transplants.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
