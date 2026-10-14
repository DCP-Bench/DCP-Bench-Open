"""Huey, Dewey and Louie: from three truthful statements, decide which of the nephews are guilty."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    model = gp.Model("huey_dewey_louie")

    # 1 when that nephew is guilty. The problem has no instance data.
    huey = model.addVar(vtype=GRB.BINARY, name="huey")
    dewey = model.addVar(vtype=GRB.BINARY, name="dewey")
    louie = model.addVar(vtype=GRB.BINARY, name="louie")

    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
    model.addConstr(dewey == louie, name="huey_says")

    # Dewey: if Huey is guilty, then so am I.
    model.addConstr(huey <= dewey, name="dewey_says")

    # Louie: Dewey and I are not both guilty.
    model.addConstr(dewey + louie <= 1, name="louie_says")

    return model, {"huey": huey, "dewey": dewey, "louie": louie}
