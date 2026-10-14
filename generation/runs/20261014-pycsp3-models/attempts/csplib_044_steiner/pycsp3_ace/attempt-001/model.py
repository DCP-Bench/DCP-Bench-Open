from pycsp3 import *

# Ternary Steiner system of order n: n*(n-1)/6 triples of distinct elements from 0 to n-1
# (columns are elements, counted from 0), such that any two triples have at most one common element.
n = data.n
b = n * (n - 1) // 6
pairs = [(j, l) for j in range(n) for l in range(j + 1, n)]

# sets[i][j] is 1 when element j is part of triple i
sets = VarArray(size=[b, n], dom={0, 1})

# covered[i][p] is 1 when triple i contains both elements of pair p
covered = VarArray(size=[b, len(pairs)], dom={0, 1})

satisfy(
    # each triple has exactly three distinct elements
    [Sum(sets[i]) == 3 for i in range(b)],
    # the flag says whether a triple holds both elements of a pair
    [(covered[i][p] == 1) == (Sum(sets[i][j], sets[i][l]) == 2)
     for i in range(b) for p, (j, l) in enumerate(pairs)],
    # two triples share at most one element, so each pair of elements lies in at most one triple
    [Sum(covered[i][p] for i in range(b)) <= 1 for p in range(len(pairs))],
)
