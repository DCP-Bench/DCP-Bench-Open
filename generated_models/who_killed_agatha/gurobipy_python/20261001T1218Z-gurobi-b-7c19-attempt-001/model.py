"""Who killed Agatha: deduce the killer among the residents of Dreadsbury Mansion."""
import gurobipy as gp
from gurobipy import GRB

# The roles belong to the problem: Agatha, the butler and Charles are the
# first three residents in the instance's list of names.
AGATHA, BUTLER, CHARLES = 0, 1, 2


def build(instance):
    names = instance["names"]
    n = len(names)
    people = range(n)
    victim = AGATHA

    model = gp.Model("who_killed_agatha")

    # hates[i, j] = 1 when i hates j; richer[i, j] = 1 when i is richer than j.
    hates = model.addVars(n, n, vtype=GRB.BINARY, name="hates")
    richer = model.addVars(n, n, vtype=GRB.BINARY, name="richer")

    # is_killer[i] = 1 when i killed Agatha; someone did.
    is_killer = model.addVars(n, vtype=GRB.BINARY, name="is_killer")
    model.addConstr(is_killer.sum() == 1, name="one_killer")

    # A killer always hates, and is no richer than, his victim.
    for i in people:
        model.addConstr(is_killer[i] <= hates[i, victim], name=f"killer_hates[{i}]")
        model.addConstr(is_killer[i] <= 1 - richer[i, victim], name=f"killer_not_richer[{i}]")

    # No one is richer than himself, and of two people exactly one is richer.
    for i in people:
        model.addConstr(richer[i, i] == 0, name=f"not_richer_than_self[{i}]")
        for j in range(i + 1, n):
            model.addConstr(richer[i, j] == 1 - richer[j, i], name=f"richer_antisymmetric[{i},{j}]")

    # Charles hates no one that Agatha hates.
    for i in people:
        model.addConstr(hates[AGATHA, i] + hates[CHARLES, i] <= 1, name=f"charles[{i}]")

    # Agatha hates everybody except the butler.
    for i in people:
        model.addConstr(hates[AGATHA, i] == (0 if i == BUTLER else 1), name=f"agatha[{i}]")

    # The butler hates everyone not richer than Aunt Agatha.
    for i in people:
        model.addConstr(1 - richer[i, AGATHA] <= hates[BUTLER, i], name=f"butler_poorer[{i}]")

    # The butler hates everyone whom Agatha hates.
    for i in people:
        model.addConstr(hates[AGATHA, i] <= hates[BUTLER, i], name=f"butler_agatha[{i}]")

    # No one hates everyone.
    for i in people:
        model.addConstr(hates.sum(i, "*") <= n - 1, name=f"not_everyone[{i}]")

    killer = gp.quicksum(i * is_killer[i] for i in people)
    return model, {"killer": killer}
