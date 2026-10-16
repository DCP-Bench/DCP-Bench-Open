# Car selection: assign participants to cars they are interested in, with at most one car per participant and at most one participant per car, maximising the number of assignments.
from pycsp3 import *

interest = data.possible_assignments
n = len(interest)
m = len(interest[0])

# assignments[i][j] = 1 if participant i is assigned to car j
assignments = VarArray(size=[n, m], dom={0, 1})

satisfy(
    # a participant is assigned only to a car that the participant is interested in
    [assignments[i][j] <= interest[i][j] for i in range(n) for j in range(m)],
    # each participant is assigned to at most one car
    [Sum(assignments[i][j] for j in range(m)) <= 1 for i in range(n)],
    # each car is assigned to at most one participant
    [Sum(assignments[i][j] for i in range(n)) <= 1 for j in range(m)],
)

# maximise the total number of assignments
maximize(Sum(assignments[i][j] for i in range(n) for j in range(m)))
