# Contracting costs: six tradesmen are paid in pairs, and the payments to each
# pair are known. Find what each man charges.
from exact import Exact

NAMES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
# (first man, second man, dollars paid to the two together)
PAYMENTS = [("paper_hanger", "painter", 1100), ("painter", "plumber", 1700),
            ("plumber", "electrician", 1100), ("electrician", "carpenter", 3300),
            ("carpenter", "mason", 5300), ("mason", "painter", 3200)]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    # A man charges at least a dollar, so he charges less than any payment he is part of.
    for name in NAMES:
        top = min(pay for a, b, pay in PAYMENTS if name in (a, b)) - 1
        solver.addVariable(name, 1, top)

    # The two men of a pair are paid the given amount together.
    for a, b, pay in PAYMENTS:
        solver.addConstraint([(1, a), (1, b)], True, pay, True, pay)

    return solver, {name: name for name in NAMES}
