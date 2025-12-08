#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob044_steiner.py
# Source description: https://www.csplib.org/Problems/prob044/

"""
The ternary Steiner problem of order \( n \) consists of finding a set of \( n \cdot (n-1)/6 \) triples of distinct
integer elements in \(\{1, \ldots, n\}\) such that any two triples have at most one common element. It is a hypergraph
problem coming from combinatorial mathematics where \( n \) modulo 6 has to be equal to 1 or 3.
One possible solution for \( n = 7 \) is \(\{\{1, 2, 3\}, \{1, 4, 5\}, \{1, 6, 7\}, \{2, 4, 6\},
\{2, 5, 7\}, \{3, 4, 7\}, \{3, 5, 6\}\}\). The solution contains \( 7 \cdot (7-1)/6 = 7 \) triples.
This is a particular case of the more general Steiner system.

Print the set of triples (sets) as a boolean matrix where each row represents a triple and each column represents an
element. The value of the matrix at position [i, j] is true if element j is part of triple i, and false otherwise.
"""

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
