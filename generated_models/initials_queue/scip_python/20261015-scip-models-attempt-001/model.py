# Initials queue: find the initials of the first ten people in a Maths lecture queue, where
# each person's initials are an alphabetically ordered pair of distinct letters from A-E.
from itertools import combinations

from pyscipopt import Model, quicksum

# The problem fixes the letters A to E as 0 to 4 and says each initial pair is an ordered
# pair of distinct letters from them, so the 10 possible pairs are all 2-subsets of {0..4}.
LETTERS = range(5)
PAIRS = list(combinations(LETTERS, 2))
QUEUE_LENGTH = 10


def build(instance):
    m = Model()
    P = range(len(PAIRS))
    N = range(QUEUE_LENGTH)

    # x[i, p] = 1 if the person at position i (from the front) has the initials PAIRS[p]
    x = {(i, p): m.addVar(name=f"x_{i}_{p}", vtype="B") for i in N for p in P}

    # each queue position holds exactly one pair of initials
    for i in N:
        m.addCons(quicksum(x[i, p] for p in P) == 1)

    # no two people share the same initials: each of the 10 pairs is used exactly once
    for p in P:
        m.addCons(quicksum(x[i, p] for i in N) == 1)

    # no-one shares a letter with the person in front of them:
    # for each letter v, the person at position i and the person at position i+1 together
    # hold v at most once
    for i in range(QUEUE_LENGTH - 1):
        for v in LETTERS:
            m.addCons(
                quicksum(x[i, p] + x[i + 1, p] for p in P if v in PAIRS[p]) <= 1
            )

    # Mathematician BE is at the front of the queue
    m.addCons(x[0, PAIRS.index((1, 4))] == 1)
    # with CD right behind
    m.addCons(x[1, PAIRS.index((2, 3))] == 1)
    # and BD right at the end of the queue
    m.addCons(x[QUEUE_LENGTH - 1, PAIRS.index((1, 3))] == 1)

    # the output gives the initials of each position from the front, as letter numbers 0 to 4
    queue = [
        [
            quicksum(PAIRS[p][0] * x[i, p] for p in P),
            quicksum(PAIRS[p][1] * x[i, p] for p in P),
        ]
        for i in N
    ]
    return m, {"queue": queue}
