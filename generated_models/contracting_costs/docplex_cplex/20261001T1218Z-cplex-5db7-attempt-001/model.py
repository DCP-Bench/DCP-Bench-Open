"""Contracting costs (Sam Loyd): from what a contractor pays to pairs of tradesmen, find what
each man charges.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Each charge is 1..5300 dollars, the range the
    # reference declares; 5300 is the largest payment in the statement.
    model = Model("contracting_costs")
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
    charge = {name: model.integer_var(1, 5300, name=name) for name in names}

    # The contractor pays, for each pair, the sum of the two men's charges:
    # paper hanger and painter $1100, painter and plumber $1700, plumber and electrician
    # $1100, electrician and carpenter $3300, carpenter and mason $5300, mason and painter
    # $3200.
    payments = [("paper_hanger", "painter", 1100),
                ("painter", "plumber", 1700),
                ("plumber", "electrician", 1100),
                ("electrician", "carpenter", 3300),
                ("carpenter", "mason", 5300),
                ("mason", "painter", 3200)]
    for first, second, total in payments:
        model.add_constraint(charge[first] + charge[second] == total)

    return model, dict(charge)
