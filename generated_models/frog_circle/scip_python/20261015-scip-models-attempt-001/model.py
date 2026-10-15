# Frog circle: arrange cards 1..n on a circle so that a frog starting on card 1 and
# jumping k places clockwise from card k visits every card.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()

    # b[p, v]: the card at place p (0-based positions around the circle) is v
    b = {(p, v): m.addVar(name=f"b_{p}_{v}", vtype="B") for p in range(n) for v in range(1, n + 1)}
    # each place holds exactly one card
    for p in range(n):
        m.addCons(quicksum(b[p, v] for v in range(1, n + 1)) == 1)
    # each card is used exactly once
    for v in range(1, n + 1):
        m.addCons(quicksum(b[p, v] for p in range(n)) == 1)

    # T[p, k] = 1 when the frog stands on place p at step k (k = 0 is the start);
    # every place is visited at exactly one step, so the steps form a permutation
    T = {(p, k): m.addVar(name=f"T_{p}_{k}", vtype="B") for p in range(n) for k in range(n)}
    for p in range(n):
        m.addCons(quicksum(T[p, k] for k in range(n)) == 1)
    for k in range(n):
        m.addCons(quicksum(T[p, k] for p in range(n)) == 1)
    # the frog starts on card 1, which is the first place of the arrangement
    m.addCons(T[0, 0] == 1)
    m.addCons(b[0, 1] == 1)

    # the frog visits every card: from the place visited at step k, the jump lands on the
    # place visited at step k+1, for k = 0..n-2 (the jump after the last card is unconstrained)
    # a jump from place p by card v lands on place q = (p + v) mod n
    for p in range(n):
        for v in range(1, n + 1):
            q = (p + v) % n
            for k in range(n - 1):
                # if the frog is on place p at step k with card v there, then it is on q at step k+1
                m.addCons(T[q, k + 1] >= T[p, k] + b[p, v] - 1)

    # the output is the card at each place, in place order
    x = [quicksum(v * b[p, v] for v in range(1, n + 1)) for p in range(n)]
    return m, {"x": x}
