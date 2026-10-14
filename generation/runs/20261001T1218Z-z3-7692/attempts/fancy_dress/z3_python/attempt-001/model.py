# Fancy dress: Mr Greenguest must wear green to a dress party. Choose which of
# tie, hat, shirt and socks he wears in green, and whether he pays the entrance
# fee for breaking the dress rules, at the lowest cost.
import z3


def build(instance):
    del instance  # the puzzle states its own prices and rules

    # t: green tie, h: green hat, r: green shirt, s: green socks,
    # n: pays the entrance fee.
    t, h, r, s, n = z3.Bools("t h r s n")

    solver = z3.Solver()

    # Rule 1: a green tie requires a green shirt, unless the entrance fee is paid.
    solver.add(z3.Or(z3.Implies(t, r), n))

    # Rule 2: green socks or a green shirt are only allowed together with a green
    # tie or a green hat, unless the entrance fee is paid.
    solver.add(z3.Or(z3.Implies(z3.Or(s, r), z3.Or(t, h)), n))

    # Rule 3: a green shirt, a green hat, or socks that are not green require a
    # green tie, unless the entrance fee is paid.
    solver.add(z3.Or(z3.Implies(z3.Or(r, h, z3.Not(s)), t), n))

    # Cost: tie $10, hat $2, socks $12, entrance fee $11. The shirt costs nothing
    # because he already owns one.
    cost = z3.If(t, 10, 0) + z3.If(h, 2, 0) + z3.If(s, 12, 0) + z3.If(n, 11, 0)

    return solver, {"t": t, "h": h, "r": r, "s": s, "n": n}, ("minimize", cost)
