# Contracting costs: find what each of six tradesmen (paper hanger, painter,
# plumber, electrician, carpenter, mason) charges, given the payments the
# contractor makes for each pair of them.
from pyscipopt import Model, quicksum

# The payments for each pair of workers, as stated in the problem description.
# The instance carries no fields, so these numbers are the problem's own data.
PAIR_PAYMENTS = [
    (("paper_hanger", "painter"), 1100),
    (("painter", "plumber"), 1700),
    (("plumber", "electrician"), 1100),
    (("electrician", "carpenter"), 3300),
    (("carpenter", "mason"), 5300),
    (("mason", "painter"), 3200),
]

WORKERS = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]


def build(instance):
    m = Model()
    # Charges are dollar amounts, so they are nonnegative integers.
    # Each charge is a summand of one pair payment, so it cannot exceed the largest payment.
    ub = max(amount for _, amount in PAIR_PAYMENTS)
    x = {w: m.addVar(name=w, vtype="I", lb=0, ub=ub) for w in WORKERS}

    # each pair's two charges add up to the payment the contractor makes for that pair
    for (a, b), amount in PAIR_PAYMENTS:
        m.addCons(x[a] + x[b] == amount, name=f"pay_{a}_{b}")

    # satisfaction problem: any assignment that meets all payments is a solution
    outputs = {w: x[w] for w in WORKERS}
    return m, outputs
