# The handshaking problem: Hilary and Jocelyn (married) invite num_couples couples to dinner. Guests
# shake hands, but nobody shakes hands with themselves or their spouse. Jocelyn asks everybody how
# many hands they shook and gets different answers from everyone but Hilary. How many hands did
# Hilary shake?
from exact import Exact


def build(instance):
    num_couples = instance["num_couples"]  # couples invited, not counting Hilary and Jocelyn
    n = 2 + num_couples * 2  # people, numbered so that person 2c and 2c+1 are spouses
    # Person 0 is Hilary and person 1 is Jocelyn (their spouse), as in the reference.

    solver = Exact()

    # shakes[i, j] = 1 (i < j) when persons i and j shake hands. One variable per unordered pair
    # makes "a shakes hands with b <-> b shakes hands with a" hold by construction; spouses
    # (2c, 2c+1) never shake hands, so they get no variable.
    shakes = {}
    for i in range(n):
        for j in range(i + 1, n):
            if not (i % 2 == 0 and j == i + 1):
                shakes[i, j] = f"shakes_{i}_{j}"
                solver.addVariable(shakes[i, j], 0, 1)

    # x[i] is the number of hands person i shook: at most n - 2, since nobody shakes their own
    # hand or their spouse's
    x = [f"x_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(x[i], 0, n - 2)
        hands = [(1, name) for (a, b), name in shakes.items() if i in (a, b)]
        solver.addConstraint(hands + [(-1, x[i])], True, 0, True, 0)

    # Everybody except Hilary gave a different answer. The answers are n - 1 numbers in 0..n-2,
    # so each count is used exactly once. Exact has no all-different constraint, so
    # counts_is[i][v] = 1 when person i shook v hands, and each count is used by at most one person.
    counts_is = {}
    for i in range(1, n):
        for v in range(n - 1):
            counts_is[i, v] = f"person_{i}_shook_{v}"
            solver.addVariable(counts_is[i, v], 0, 1)
        solver.addConstraint([(1, counts_is[i, v]) for v in range(n - 1)], True, 1, True, 1)
        solver.addConstraint([(v, counts_is[i, v]) for v in range(1, n - 1)] + [(-1, x[i])],
                             True, 0, True, 0)
    for v in range(n - 1):
        solver.addConstraint([(1, counts_is[i, v]) for i in range(1, n)], False, 0, True, 1)

    # hil is the number of hands Hilary shook
    return solver, {"hil": x[0]}
