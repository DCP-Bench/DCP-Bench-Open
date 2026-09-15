import cpmpy as cp


def build(instance):
    """Contracting costs: six tradesmen, six pairwise bills.

    The puzzle states its own six bills, so `instance` is unused.
    """
    del instance

    n = 6
    x = cp.intvar(1, 5300, shape=n, name="x")
    paper_hanger, painter, plumber, electrician, carpenter, mason = x

    bills = [
        (paper_hanger, painter, 1100),
        (painter, plumber, 1700),
        (plumber, electrician, 1100),
        (electrician, carpenter, 3300),
        (carpenter, mason, 5300),
        (mason, painter, 3200),
    ]

    model = cp.Model([first + second == total for first, second, total in bills])

    return model, {
        "paper_hanger": paper_hanger, "painter": painter, "plumber": plumber,
        "electrician": electrician, "carpenter": carpenter, "mason": mason,
    }
