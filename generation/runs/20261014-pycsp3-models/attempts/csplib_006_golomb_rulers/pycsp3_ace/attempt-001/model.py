from pycsp3 import *

# A Golomb ruler with m marks: the marks a_1 = 0 < a_2 < ... < a_m are such that
# all the differences a_j - a_i for i < j are distinct. Find the ruler of minimum length.

m = data.size

# the upper bound m * m on the length is a loose bound for a Golomb ruler
max_length = m * m

# marks[k] is the position of the (k+1)-th mark on the ruler
marks = VarArray(size=m, dom=range(0, max_length + 1))

# length is the position of the last mark
length = Var(dom=range(0, max_length + 1))

satisfy(
    # the first mark is at position 0
    marks[0] == 0,

    # the marks are placed in strictly increasing order
    Increasing(marks, strict=True),

    # the length of the ruler is the position of the last mark
    length == marks[m - 1],

    # all the differences between pairs of marks are distinct
    AllDifferent([marks[j] - marks[i] for i in range(m) for j in range(i + 1, m)]),
)

# minimise the length of the ruler
minimize(length)
