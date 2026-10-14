"""Huey, Dewey and Louie: from the three nephews' true statements, decide who is guilty.

The model reports whether each of huey, dewey and louie is guilty (1) or not (0).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    problem = pulp.LpProblem("huey_dewey_louie", pulp.LpMinimize)  # satisfaction

    huey = pulp.LpVariable("huey", cat="Binary")
    dewey = pulp.LpVariable("dewey", cat="Binary")
    louie = pulp.LpVariable("louie", cat="Binary")

    # Huey: Dewey and Louie have equal share in it; if one is guilty, so is the other
    problem += dewey == louie
    # Dewey: if Huey is guilty, then so am I
    problem += huey <= dewey
    # Louie: Dewey and I are not both guilty
    problem += dewey + louie <= 1

    return problem, {"huey": huey, "dewey": dewey, "louie": louie}
