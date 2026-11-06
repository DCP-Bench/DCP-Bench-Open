#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob044_steiner.py
# Source description: https://www.csplib.org/Problems/prob044/

# Data
n = 7  # Order of the Steiner Triple System
# End of data

# Import libraries
import json
from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def steiner(n):
    assert n % 6 == 1 or n % 6 == 3, "N must be (1|3) modulo 6"

    n_sets = int(n * (n - 1) // 6)

    model = Model()

    # boolean representation of sets
    # sets[i,j] = true iff item j is part of set i
    sets = boolvar(shape=(n_sets, n), name="sets")

    # cardinality of set if 3
    # can be written cleaner, see issue #117
    # model += sum(sets, axis=0) == 3
    model += [sum(s) == 3 for s in sets]

    # cardinality of intersection <= 1
    for s1, s2 in all_pairs(sets):
        model += sum(s1 & s2) <= 1

    # symmetry breaking
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # model += (sets[(0, 0)] == 1)
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (sets,)

# Example usage
model, (sets,) = steiner(n)
model.solve()

# Print
solution = {"sets": sets.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
