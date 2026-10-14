# Contracting costs: from what the contractor pays to pairs of tradesmen, find what each one
# charges.
from pychoco.model import Model

# The puzzle has no instance data; the pairwise payments are its statement. Each charge is at
# least $1 and at most the largest pairwise payment ($5,300), as in the reference.
TRADES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
PAYMENTS = [
    ("paper_hanger", "painter", 1100),
    ("painter", "plumber", 1700),
    ("plumber", "electrician", 1100),
    ("electrician", "carpenter", 3300),
    ("carpenter", "mason", 5300),
    ("mason", "painter", 3200),
]


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    top = max(amount for _, _, amount in PAYMENTS)
    # charge[t] = what tradesman t charges, in dollars
    charge = {t: model.intvar(1, top, name=t) for t in TRADES}

    # Each pair of tradesmen together is paid the stated amount.
    for first, second, amount in PAYMENTS:
        model.arithm(charge[first], "+", charge[second], "=", amount).post()

    return model, charge
