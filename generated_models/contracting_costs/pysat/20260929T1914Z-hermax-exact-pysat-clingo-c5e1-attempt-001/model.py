# Contracting costs: six tradesmen are paid in pairs, and the payments to each
# pair are known. Find what each man charges.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

NAMES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
# (first man, second man, dollars paid to the two together)
PAYMENTS = [("paper_hanger", "painter", 1100), ("painter", "plumber", 1700),
            ("plumber", "electrician", 1100), ("electrician", "carpenter", 3300),
            ("carpenter", "mason", 5300), ("mason", "painter", 3200)]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # A man charges at least a dollar, so he charges less than any payment he is part of.
    top = {name: min(pay for a, b, pay in PAYMENTS if name in (a, b)) - 1 for name in NAMES}
    charge = {name: Integer(name, 1, top[name], vpool=pool) for name in NAMES}
    engine = IntegerEngine(vars=list(charge.values()), vpool=pool)
    cnf = engine.clausify()

    # The two men of a pair are paid the given amount together: whatever the first
    # charges, the second charges the rest.
    for a, b, pay in PAYMENTS:
        for value in range(1, top[a] + 1):
            rest = pay - value
            if 1 <= rest <= top[b]:
                cnf.append([-charge[a].equals(value), charge[b].equals(rest)])
            else:
                cnf.append([-charge[a].equals(value)])

    return cnf, charge
