from pycsp3 import *

v = data.v
b = data.b
r = data.r
k = data.k
l = data.l

# the incidence matrix: rows are the v objects, columns are the b blocks, 1 when the object is in the block
matrix = VarArray(size=[v, b], dom={0, 1})

satisfy(
    # each object occurs in exactly r blocks
    [Sum(matrix[i]) == r for i in range(v)],
    # each block contains exactly k objects
    [Sum(matrix[i][j] for i in range(v)) == k for j in range(b)],
)

# every two distinct objects occur together in exactly lambda blocks
for i in range(v):
    for i2 in range(i + 1, v):
        satisfy(
            Sum(matrix[i][j] * matrix[i2][j] for j in range(b)) == l
        )

# the rows of the incidence matrix are in lexicographic order, to break the symmetry between objects
satisfy(LexIncreasing(matrix))
