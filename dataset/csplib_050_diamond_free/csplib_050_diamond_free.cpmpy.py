#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob050_diamond_free.py
# Source description: https://www.csplib.org/Problems/prob050/

"""
Given a simple undirected graph \( G = (V, E) \), where \( V \) is the set of vertices and \( E \) the set of undirected edges,
the edge \(\{u, v\}\) is in \( E \) if and only if vertex \( u \) is adjacent to vertex \( v \in G \). The graph is simple in
that there are no loop edges, i.e., we have no edges of the form \(\{v, v\}\). Each vertex \( v \in V \) has a degree \( d_v \)
i.e., the number of edges incident on that vertex. Consequently, a graph has a degree sequence \( d_1, \ldots, d_n \), where
\( d_i \geq d_{i+1} \). A diamond is a set of four vertices in \( V \) such that there are at least five edges between those
vertices. Conversely, a graph is diamond-free if it has no diamond as an induced subgraph, i.e., for every set of four vertices
the number of edges between those vertices is at most four.

In our problem, we have additional properties required of the degree sequences of the graphs, in particular, that the degree
of each vertex is greater than zero (i.e., isolated vertices are disallowed), the degree of each vertex is modulo 3, and the
sum of the degrees is modulo 12 (i.e., \(|E|\) is modulo 6).

The problem is then for a given value of \( n \), produce all unique degree sequences \( d_1, \ldots, d_n \) such that

- \( d_i \geq d_{i+1} \)
- Each degree \( d_i > 0 \) and \( d_i \) is modulo 3
- The sum of the degrees is modulo 12
- There exists a simple diamond-free graph with that degree sequence

Print the adjacency matrix of the graph (matrix) as a list of lists of booleans.
"""

# Data
N = 10  # Number of vertices in the graph
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *
from itertools import combinations

def diamond_free(N):
    # By definition a and b will have the same cardinality:
    matrix = boolvar(shape=(N, N), name="matrix")

    model = Model()

    # No rows contain just zeroes.
    model += [sum(row) > 0 for row in matrix] # can be written cleaner, see issue #117
    # Every row has a sum modulo 3.
    model += [sum(row) % 3 == 0 for row in matrix]
    # The sum of the matrix is modulo 12.
    model += sum(matrix) % 12 == 0
    # No row R contains a 1 in its Rth column.
    model += [matrix[np.diag_indices(N)] == 0]

    # Every grouping of 4 rows can have at most a sum of 4 between them.
    for a, b, c, d in combinations(range(N), 4):
        model += sum([matrix[a][b], matrix[a][c], matrix[a][d],
                      matrix[b][c], matrix[b][d], matrix[c][d]]) <= 4

    # Undirected graph
    model += matrix == matrix.T

    # Symmetry breaking
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # # lexicographic ordering of rows
    # for r in range(N - 1):
    #     b = boolvar(N + 1)
    #     model += b[0] == 1
    #     model += b == ((matrix[r] <= matrix[r + 1]) &
    #                    ((matrix[r] < matrix[r + 1]) | b[1:] == 1))
    #     model += b[-1] == 0
    # # lexicographic ordering of cols
    # for c in range(N - 1):
    #     b = boolvar(N + 1)
    #     model += b[0] == 1
    #     model += b == ((matrix.T[c] <= matrix.T[c + 1]) &
    #                    ((matrix.T[c] < matrix.T[c + 1]) | b[1:] == 1))
    #     model += b[-1] == 0
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, matrix

# Example usage
model, matrix = diamond_free(N)
model.solve()

# Print
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
