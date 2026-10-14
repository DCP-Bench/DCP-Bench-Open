# Best host: seat six guests round a table so that everyone sits only next to
# guests they get along with.
from exact import Exact

# prefs[g] = the guests g is willing to sit next to; 0 Andrew, 1 Betty, 2 Cara,
# 3 Dave, 4 Erica, 5 Frank
PREFS = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = len(PREFS)
    solver = Exact()
    # sits[i][g] = 1 when guest g has seat i, going round the table
    sits = [[f"seat_{i}_guest_{g}" for g in range(n)] for i in range(n)]
    for i in range(n):
        for name in sits[i]:
            solver.addVariable(name, 0, 1)
        # a seat holds one guest
        solver.addConstraint([(1, name) for name in sits[i]], True, 1, True, 1)
    # every guest gets one seat
    for g in range(n):
        solver.addConstraint([(1, sits[i][g]) for i in range(n)], True, 1, True, 1)

    # Two guests in neighbouring seats must each be willing to sit next to the other:
    # forbid every pair of neighbours that is not compatible.
    for i in range(n):
        j = (i + 1) % n
        for a in range(n):
            for b in range(n):
                if b not in PREFS[a] or a not in PREFS[b]:
                    solver.addConstraint([(1, sits[i][a]), (1, sits[j][b])], False, 0, True, 1)

    # x[i] = the guest at seat i
    x = [f"x_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(x[i], 0, n - 1)
        solver.addConstraint([(g, sits[i][g]) for g in range(1, n)] + [(-1, x[i])], True, 0, True, 0)

    return solver, {"x": x}
