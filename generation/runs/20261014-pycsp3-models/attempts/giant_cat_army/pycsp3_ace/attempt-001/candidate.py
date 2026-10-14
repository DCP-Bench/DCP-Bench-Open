from pycsp3 import *

# Giant cat army: build a list starting at 0 with the operations add 5, add 7 or take the
# square root (only for a perfect square). The list has 24 distinct integers, all at most 60,
# ends with 14, and contains 2, 10 and 14 in that order.
length = 24
max_value = 60

# x[i] is the i-th element of the list
x = VarArray(size=length, dom=range(0, max_value + 1))

# the position of 2 and the position of 10 in the list
pos2 = Var(dom=range(length))
pos10 = Var(dom=range(length))

# each step of the list is one of the three operations: add 5, add 7, or take the square root
steps = ([(a, a + 5) for a in range(max_value + 1) if a + 5 <= max_value]
         + [(a, a + 7) for a in range(max_value + 1) if a + 7 <= max_value]
         + [(s * s, s) for s in range(8) if s * s <= max_value])

satisfy(
    # the list starts with 0
    x[0] == 0,
    # the list ends with 14
    x[length - 1] == 14,
    # all elements are distinct
    AllDifferent(x),
    # each element follows from the one before by one of the operations
    [Table(scope=[x[i], x[i + 1]], supports=steps) for i in range(length - 1)],
    # the list holds 2, then 10, then 14 in that order
    x[pos2] == 2,
    x[pos10] == 10,
    pos2 < pos10,
    pos10 < length - 1,
)
