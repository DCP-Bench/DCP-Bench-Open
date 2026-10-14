# Problem: Assign each task to exactly one person at the lowest total cost, with each person taking at most one task.
from pycsp3 import *

cost = data.cost
T = len(cost)
P = len(cost[0])
# x[i][j] = 1 if task i is assigned to person j
x = VarArray(size=[T, P], dom={0, 1})
satisfy(
    # each task must be assigned to exactly one person
    [Sum(x[i]) == 1 for i in range(T)],
    # each person takes at most one task
    [Sum(x[:, j]) <= 1 for j in range(P)],
)
# the total cost is minimized
minimize(Sum(cost[i][j] * x[i][j] for i in range(T) for j in range(P)))
