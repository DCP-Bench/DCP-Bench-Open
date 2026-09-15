from ortools.sat.python import cp_model


def build(instance):
    """Contracting costs: six tradesmen, six pairwise bills.

    The puzzle states its own six bills, so `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    names = [
        "paper_hanger", "painter", "plumber",
        "electrician", "carpenter", "mason",
    ]
    x = [model.new_int_var(1, 5300, name) for name in names]
    paper_hanger, painter, plumber, electrician, carpenter, mason = x

    bills = [
        (paper_hanger, painter, 1100),
        (painter, plumber, 1700),
        (plumber, electrician, 1100),
        (electrician, carpenter, 3300),
        (carpenter, mason, 5300),
        (mason, painter, 3200),
    ]
    for first, second, total in bills:
        model.add(first + second == total)

    return model, dict(zip(names, x))
