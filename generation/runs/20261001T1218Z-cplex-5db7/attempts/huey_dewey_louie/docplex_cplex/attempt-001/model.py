"""Huey, Dewey and Louie: from three truthful statements, decide which of them are guilty."""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data.
    model = Model("huey_dewey_louie")

    # 1 means guilty.
    huey = model.binary_var(name="huey")
    dewey = model.binary_var(name="dewey")
    louie = model.binary_var(name="louie")

    # Huey: Dewey and Louie share equally; if one is guilty, so is the other.
    model.add_constraint(dewey == louie)
    # Dewey: if Huey is guilty, then so am I.
    model.add_constraint(huey <= dewey)
    # Louie: Dewey and I are not both guilty.
    model.add_constraint(dewey + louie <= 1)

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
