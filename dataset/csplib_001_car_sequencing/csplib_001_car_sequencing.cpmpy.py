#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/car_sequencing.ipynb
# Source description: https://www.csplib.org/Problems/prob001/
# Problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob001_car_sequence.json

"""
A number of cars are to be produced; they are not identical, because different
options are available as variants on the basic model.
The assembly line has different stations which install the various options
(air-conditioning, sunroof, etc.).
These stations have been designed to handle at most a certain percentage of
 the cars passing along the assembly line.
Furthermore, the cars requiring a certain option must not be bunched together,
otherwise the station will not be able to cope.
Consequently, the cars must be arranged in a sequence so that the capacity of
each station is never exceeded.
For instance, if a particular station can only cope with at most half of the
cars passing along the line, the sequence must be built so that at most 1 car
in any 2 requires that option.

Print the sequence of car types in the assembly line (sequence);
each car type is represented by a number starting from 0.
"""

# Data
at_most = [1, 2, 2, 2, 1]  # The amount of times a property can be present
# in a group of consecutive timeslots (see next variable)
per_slots = [2, 3, 3, 5, 5]  # The amount of consecutive timeslots
demand = [1, 1, 2, 2, 2, 2]  # The demand per type of car
requires = [[1, 0, 1, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0]]  # The properties per type of car
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n_cars = sum(demand)  # The amount of cars to sequence
n_options = len(at_most)  # The amount of different options
n_types = len(demand)  # The amount of different car types
requires = cpm_array(requires)  # For element constraint

# Decision Variables
sequence = intvar(0, n_types - 1, shape=n_cars, name="sequence")  # The sequence of car types
setup = boolvar(shape=(n_cars, n_options), name="setup")  # Sequence of different options based on the car type

# Model
model = Model()

# The amount of each type of car in the sequence has to be equal to the demand for that type
model += [sum(sequence == t) == demand[t] for t in range(n_types)]

# Make sure that the options in the setup table correspond to those of the car type
for s in range(n_cars):
    model += [setup[s, o] == requires[sequence[s], o] for o in range(n_options)]

# Check that no more than "at most" car options are used per "per_slots" slots
for o in range(n_options):
    for s in range(n_cars - per_slots[o] + 1):
        slot_range = range(s, s + per_slots[o])
        model += (sum(setup[slot_range, o]) <= at_most[o])

# Solve
model.solve()

# Print
solution = {"sequence": sequence.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
