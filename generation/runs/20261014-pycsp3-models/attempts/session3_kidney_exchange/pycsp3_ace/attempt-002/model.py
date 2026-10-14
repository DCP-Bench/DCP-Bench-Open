from pycsp3 import *

# Kidney exchange: n people on a waiting list; compatible[i] is the set of people that person i can
# donate to (people are numbered from 1 in the instance). Anyone who gives a kidney must receive one,
# and no person receives more than one kidney. Maximise the number of people that receive a kidney.
n = data.num_people
compatible = data["compatible"]

# transplants[i][j] is 1 iff person i donates to person j (0-based indices here)
transplants = VarArray(size=[n, n], dom={0, 1})

# succ[i] is the person that i donates to; succ[i] == i means that i takes no part in an exchange
succ = VarArray(size=n, dom=range(n))

# participates[i] is 1 iff person i gives and receives a kidney
participates = VarArray(size=n, dom={0, 1})

satisfy(
    # nobody donates to himself or herself, and a person donates only to people compatible with him or her
    [transplants[i][j] == 0 for i in range(n) for j in range(n) if i == j or (j + 1) not in compatible[i]],
    # a donation is recorded in transplants exactly when the donor's successor is the recipient
    [(transplants[i][j] == 1) == (succ[i] == j) for i in range(n) for j in range(n) if j != i],
    # no person receives more than one kidney, and the exchanges form disjoint cycles
    AllDifferent(succ),
    # anyone who gives a kidney must receive one: a person in an exchange has a donor and a recipient
    [Sum(transplants[i]) == Sum(transplants[j][i] for j in range(n)) for i in range(n)],
    # a person takes part in an exchange exactly when he or she gives a kidney
    [(participates[i] == 1) == (succ[i] != i) for i in range(n)],
    [Sum(transplants[i]) == participates[i] for i in range(n)],
)

# the number of people that receive a kidney is as large as possible
maximize(Sum(participates))
