import z3


def build(instance):
    """Huey, Dewey and Louie: three cub scouts who cannot lie, so each of their
    statements is simply true.
    """
    del instance

    huey, dewey, louie = z3.Bools("huey dewey louie")
    solver = z3.Solver()
    # Huey: Dewey and Louie share equally.
    solver.add(dewey == louie)
    # Dewey: if Huey is guilty, so am I.
    solver.add(z3.Implies(huey, dewey))
    # Louie: Dewey and I are not both guilty.
    solver.add(z3.Not(z3.And(dewey, louie)))

    return solver, {"huey": huey, "dewey": dewey, "louie": louie}
