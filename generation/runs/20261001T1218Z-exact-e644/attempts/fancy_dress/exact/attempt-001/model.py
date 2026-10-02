# Fancy dress: Mr Greenguest wants to enter a green-dress party at the lowest cost. He chooses
# whether to wear a green tie, hat, shirt and socks and whether to pay the entrance fee; the party
# rules about green clothes may be broken only by paying the fee.
from exact import Exact


def build(instance):
    # This problem has no instance data. The prices belong to the problem statement.
    price_tie, price_hat, price_socks, price_fee = 10, 2, 12, 11  # the shirt is already owned

    solver = Exact()
    # t = green tie, h = green hat, r = green shirt, s = green socks, n = entrance fee paid
    for name in ("t", "h", "r", "s", "n"):
        solver.addVariable(name, 0, 1)

    # Rule 1: a green tie requires a green shirt, unless the fee is paid:  t -> r or n
    solver.addConstraint([(1, "r"), (1, "n"), (-1, "t")], True, 0)
    # Rule 2: green socks or a green shirt require a green tie or a green hat, unless the fee is
    # paid:  (s or r) -> (t or h or n), stated once for s and once for r.
    solver.addConstraint([(1, "t"), (1, "h"), (1, "n"), (-1, "s")], True, 0)
    solver.addConstraint([(1, "t"), (1, "h"), (1, "n"), (-1, "r")], True, 0)
    # Rule 3: a green shirt, a green hat or no green socks require a green tie, unless the fee is
    # paid:  (r or h or not s) -> (t or n), stated once for each of the three conditions.
    solver.addConstraint([(1, "t"), (1, "n"), (-1, "r")], True, 0)
    solver.addConstraint([(1, "t"), (1, "n"), (-1, "h")], True, 0)
    solver.addConstraint([(1, "t"), (1, "n"), (1, "s")], True, 1)

    # Minimise the money spent: tie + hat + socks + entrance fee.
    cost = [(price_tie, "t"), (price_hat, "h"), (price_socks, "s"), (price_fee, "n")]
    return solver, {"t": "t", "h": "h", "r": "r", "s": "s", "n": "n"}, ("minimize", cost)
