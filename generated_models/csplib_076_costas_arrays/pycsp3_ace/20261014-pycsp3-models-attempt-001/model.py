from pycsp3 import *

# a Costas array of size n: a permutation whose difference triangle has no repeated value in any line
n = data.n
# costas[i] is the mark in column i, counted from 1
costas = VarArray(size=n, dom=range(1, n + 1))
satisfy(
    # the marks are all in different columns, one mark per row
    AllDifferent(costas),
    # each line of the difference triangle contains no value twice
    [AllDifferent([costas[i] - costas[i + l] for i in range(n - l)]) for l in range(1, n)],
)
