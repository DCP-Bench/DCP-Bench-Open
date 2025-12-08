#!/usr/bin/python3
# Category: aplai_course

"""
There are 13 people. 4 of them are male. They randomly enter a room one at a time. Find a way that the males and
females enter so that the ratio of females to males in the room at any one time is no greater than 7/3?

Print the sequence of people entering the room (sequence), as a list of booleans, where 0 represents male and 1 represents female.
"""

# Import libraries
from cpmpy import *
import json

total_people = 13
num_males = 4

# Decision variable: 0 for male, 1 for female
sequence = boolvar(shape=total_people)

# Constraints
model = Model()

# Ensure exactly number of males and females
model += [sum(sequence) == total_people - num_males]

# Add constraints for the ratio at each point in the sequence
for i in range(1, total_people):
    total_females_so_far = sum(sequence[:i])
    total_males_so_far = i - sum(sequence[:i])
    # Number of females to males is no greater than 7/3, or 3 times the females is less than or equal to 7 times the males
    model += (3 * total_females_so_far) <= (7 * total_males_so_far)

# Solve
model.solve()

# Print the solution
solution = {"sequence": sequence.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
