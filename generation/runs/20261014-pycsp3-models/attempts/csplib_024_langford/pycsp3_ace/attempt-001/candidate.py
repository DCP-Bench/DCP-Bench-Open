# Problem: Arrange the two copies of each number 1 to k so that the two copies of i are i numbers apart.
from pycsp3 import *

k = data.k
n = 2 * k
# sol[p] is the number at position p, from 1 to k
sol = VarArray(size=n, dom=range(1, k + 1))
# first_pos[i - 1] and second_pos[i - 1] are the two positions of the number i
first_pos = VarArray(size=k, dom=range(n))
second_pos = VarArray(size=k, dom=range(n))
satisfy(
    # the 2k numbers occupy 2k different positions
    AllDifferent(first_pos + second_pos),
    # the two i's appear i numbers apart: the second copy is i + 1 positions after the first
    [second_pos[i] == first_pos[i] + i + 2 for i in range(k)],
    # the first copy of each number is at its position in the sequence
    [sol[first_pos[i]] == i + 1 for i in range(k)],
    # the second copy of each number is at its position in the sequence
    [sol[second_pos[i]] == i + 1 for i in range(k)],
)
