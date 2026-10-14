# Best host: seat six guests around a round table so that every guest sits only
# next to the two guests he or she is willing to sit beside, i.e. with no conflict.
import z3


def build(instance):
    del instance  # the puzzle states its own guests and preferences

    n = 6
    Andrew, Betty, Cara, Dave, Erica, Frank = range(n)

    # Problem data (fixed by the puzzle text): prefs[g] lists the only two guests
    # that guest g will sit next to.
    prefs = [
        [Dave, Frank],   # Andrew
        [Cara, Erica],   # Betty
        [Betty, Frank],  # Cara
        [Andrew, Erica],  # Dave
        [Betty, Dave],   # Erica
        [Andrew, Cara],  # Frank
    ]

    # x[i] = the guest sitting in seat i (0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank).
    x = z3.IntVector("x", n)

    solver = z3.Solver()
    for seat in x:
        solver.add(seat >= 0, seat <= n - 1)

    # Every guest takes exactly one seat.
    solver.add(z3.Distinct(x))

    # The guests in the two seats beside seat i (the table is round) must both be
    # among the guests the person in seat i accepts as neighbours. Z3 has no Element
    # constraint, so the lookup prefs[x[i]] is spelled out for each possible guest g.
    for i in range(n):
        for g in range(n):
            for neighbour in (x[(i - 1) % n], x[(i + 1) % n]):
                solver.add(z3.Implies(x[i] == g, z3.Or([neighbour == p for p in prefs[g]])))

    return solver, {"x": list(x)}
