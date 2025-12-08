#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/crew.py
# Source description: From Gecode example crew, examples/crew.cc

"""
Assign 20 flight attendants to 10 flights. Each flight needs a certain number of cabin crew, and they have to
speak certain languages. Every cabin crew member has two flights off after an attended flight.

Print whether for each flight a person is assigned to it (crew) as a list of lists of 0/1 values, where crew[f][p] is 1 if person p is assigned to flight f, and 0 otherwise.
"""

# Data
attributes = [
    #  steward, hostess, french, spanish, german
    [1, 0, 0, 0, 1],  # Tom     = 1
    [1, 0, 0, 0, 0],  # David   = 2
    [1, 0, 0, 0, 1],  # Jeremy  = 3
    [1, 0, 0, 0, 0],  # Ron     = 4
    [1, 0, 0, 1, 0],  # Joe     = 5
    [1, 0, 1, 1, 0],  # Bill    = 6
    [1, 0, 0, 1, 0],  # Fred    = 7
    [1, 0, 0, 0, 0],  # Bob     = 8
    [1, 0, 0, 1, 1],  # Mario   = 9
    [1, 0, 0, 0, 0],  # Ed      = 10
    [0, 1, 0, 0, 0],  # Carol   = 11
    [0, 1, 0, 0, 0],  # Janet   = 12
    [0, 1, 0, 0, 0],  # Tracy   = 13
    [0, 1, 0, 1, 1],  # Marilyn = 14
    [0, 1, 0, 0, 0],  # Carolyn = 15
    [0, 1, 0, 0, 0],  # Cathy   = 16
    [0, 1, 1, 1, 1],  # Inez    = 17
    [0, 1, 1, 0, 0],  # Jean    = 18
    [0, 1, 0, 1, 1],  # Heather = 19
    [0, 1, 1, 0, 0]  # Juliet  = 20
]

# The columns are in the following order:
# staff     : Overall number of cabin crew needed
# stewards  : How many stewards are required
# hostesses : How many hostesses are required
# french    : How many French speaking employees are required
# spanish   : How many Spanish speaking employees are required
# german    : How many German speaking employees are required
required_crew = [
    [4, 1, 1, 1, 1, 1],  # Flight 1
    [5, 1, 1, 1, 1, 1],  # Flight 2
    [5, 1, 1, 1, 1, 1],  # ..
    [6, 2, 2, 1, 1, 1],
    [7, 3, 3, 1, 1, 1],
    [4, 1, 1, 1, 1, 1],
    [5, 1, 1, 1, 1, 1],
    [6, 1, 1, 1, 1, 1],
    [6, 2, 2, 1, 1, 1],  # ...
    [7, 3, 3, 1, 1, 1]  # Flight 10
]
# End of data

# Import libraries
from cpmpy import *
import json


# Parameters
num_persons = len(attributes)  # number of persons
num_flights = len(required_crew)  # number of flights

#
# declare variables
#
crew = boolvar(shape=(num_flights, num_persons), name="crew")

# number of working persons
num_working = intvar(1, num_persons, name="num_working")

#
# constraints
#
model = Model()

# number of working persons
model += [num_working == sum([sum([crew[(f, p)] for f in range(num_flights)]) >= 1
                              for p in range(num_persons)])]

for f in range(num_flights):
    # size of crew
    tmp = [crew[(f, i)] for i in range(num_persons)]
    model += [sum(tmp) == required_crew[f][0]]

    # attributes and requirements
    for j in range(5):
        tmp = [attributes[i][j] * crew[(f, i)] for i in range(num_persons)]
        model += [sum(tmp) >= required_crew[f][j + 1]]

# after a flight, break for at least two flights
for f in range(num_flights - 2):
    for i in range(num_persons):
        model += [crew[f, i] + crew[f + 1, i] + crew[f + 2, i] <= 1]

# extra contraint: all must work at least two of the flights
# for i in range(num_persons):
#     model += [sum([crew[f,i] for f in range(num_flights)]) >= 2]

# Solve the model
model.solve()

# Print the solution
solution = {"crew": crew.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
