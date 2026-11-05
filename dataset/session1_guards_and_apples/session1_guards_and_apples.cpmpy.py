#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/guards_and_apples.mzn

# Data
num_gates = 5
# End of data

# Import libraries
from cpmpy import *
import json

# Decision Variables
apples = intvar(0, 100, shape=num_gates + 1)  # the number of apples before each gate plus after the last gate

# Constraints
model = Model()

# The boy is left with no apples after giving the apple to the girl, so he has 1 apple after the last gate.
model += apples[-1] == 1

# At each guard, the boy gives half of his apples, plus one.
for i in range(1, num_gates + 1):
    has_before = apples[i - 1]
    has_after = apples[i]
    model += has_before == 2 * (has_after + 1)

# Solve
model.solve()

# Print the solution
solution = {"apples": apples.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script