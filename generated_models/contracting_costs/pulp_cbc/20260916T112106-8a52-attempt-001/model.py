import pulp


def build(instance):
    """Contracting costs: six tradesmen, six pairwise bills."""
    del instance

    problem = pulp.LpProblem("contracting", pulp.LpMinimize)
    names = ["paper_hanger", "painter", "plumber",
             "electrician", "carpenter", "mason"]
    x = {n: pulp.LpVariable(n, 1, 5300, cat="Integer") for n in names}

    for first, second, total in (
        ("paper_hanger", "painter", 1100),
        ("painter", "plumber", 1700),
        ("plumber", "electrician", 1100),
        ("electrician", "carpenter", 3300),
        ("carpenter", "mason", 5300),
        ("mason", "painter", 3200),
    ):
        problem += x[first] + x[second] == total

    return problem, x
