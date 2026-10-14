from pycsp3 import *

# Kidney exchange: n people on a waiting list; compatible[i] is the set of people that person i can
# donate to (people are numbered from 1 in the instance). Anyone who gives a kidney must receive one,
# and no person receives more than one kidney. Maximise the number of people that receive a kidney.
n = data.num_people
compatible = data["compatible"]

# transplants[i][j] is 1 iff person i donates to person j (0-based indices here)
transplants = VarArray(size=[n, n], dom={0, 1})

satisfy(
    # a person donates only to people compatible with him or her; nobody donates to himself or herself
    [transplants[i][j] == 0 for i in range(n) for j in range(n) if i == j or (j + 1) not in compatible[i]],
    # each person gives at most one kidney
    [Sum(transplants[i]) <= 1 for i in range(n)],
    # no person receives more than one kidney
    [Sum(transplants[i][j] for i in range(n)) <= 1 for j in range(n)],
    # anyone who gives a kidney must receive one: the number given equals the number received
    [Sum(transplants[i]) == Sum(transplants[j][i] for j in range(n)) for i in range(n)],
)

# the number of people that receive a kidney is as large as possible
maximize(Sum(transplants[i][j] for i in range(n) for j in range(n)))
