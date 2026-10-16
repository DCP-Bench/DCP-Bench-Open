# Problem: Order the 13 people so that at every moment the ratio of females to males is at most 7/3.
from pycsp3 import *

# 0 is a male, 1 is a female
sequence = VarArray(size=13, dom={0, 1})
satisfy(
    # there are 4 males and 9 females
    Count(sequence, value=0) == 4,
    # at every moment the females to males ratio is at most 7/3: 3 * F <= 7 * M, with F + M = k
    [10 * Sum(sequence[:k]) <= 7 * k for k in range(1, 14)],
)
