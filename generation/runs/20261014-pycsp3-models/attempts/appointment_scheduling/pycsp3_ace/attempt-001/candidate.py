from pycsp3 import *

# schedule the people into the interview slots according to their free-busy schedules
n = len(data.m)
# x[i][j] is 1 if person i is assigned to slot j
x = VarArray(size=[n, n], dom={0, 1})
satisfy(
    # each person is assigned to exactly one slot
    [Sum(x[i]) == 1 for i in range(n)],
    # each slot is given to exactly one person
    [Sum(x[:, j]) == 1 for j in range(n)],
    # a person can only be placed in a slot where they are free (m[i][j] is 1)
    [x[i][j] <= data.m[i][j] for i in range(n) for j in range(n)],
)
