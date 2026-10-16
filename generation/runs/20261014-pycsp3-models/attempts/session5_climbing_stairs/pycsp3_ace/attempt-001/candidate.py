from pycsp3 import *

# Climbing stairs: a stair of n steps is climbed in moves of m1 to m2 steps each.
# steps[k] is the size of move k, and 0 once the top is reached.

n = data.n
m1 = data.m1
m2 = data.m2

# steps[k] is 0 or a move size from m1 to m2
steps = VarArray(size=n, dom={0} | set(range(m1, m2 + 1)))

satisfy(
    # the moves add up to exactly the number of steps of the stair
    Sum(steps) == n,

    # after a move of 0 steps, the top has been reached, so every later move is 0 too
    [imply(steps[k] == 0, steps[k + 1] == 0) for k in range(n - 1)],
)
