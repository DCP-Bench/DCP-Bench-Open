from pycsp3 import *

# A golf course of 18 holes, each of length 3, 4 or 5, with a total length of 72.

# holes[k] is the length of hole k
holes = VarArray(size=18, dom={3, 4, 5})

satisfy(
    # the total length of the course is 72
    Sum(holes) == 72,
)
