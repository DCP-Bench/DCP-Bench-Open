"""Number partitioning: split 1..n into two sets of equal size with equal sums and equal sums of squares."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    half = n // 2
    values = range(1, n + 1)
    slots = range(n)  # slots 0..half-1 are the members of A, the rest those of B
    in_A = range(half)
    in_B = range(half, n)

    model = gp.Model("number_partitioning")

    # holds[s, v] is 1 when slot s holds number v. Each slot holds one number and
    # each number is in one slot, so A and B partition 1..n with n/2 each.
    holds = model.addVars(slots, values, vtype=GRB.BINARY, name="holds")
    for s in slots:
        model.addConstr(holds.sum(s, "*") == 1, name=f"slot[{s}]")
    for v in values:
        model.addConstr(holds.sum("*", v) == 1, name=f"value[{v}]")

    def total(members, power):
        return gp.quicksum(v ** power * holds[s, v] for s in members for v in values)

    # The numbers in A add up to the same sum as those in B.
    model.addConstr(total(in_A, 1) == total(in_B, 1), name="sums")

    # So do their squares; with one-hot slots a square is a constant coefficient.
    model.addConstr(total(in_A, 2) == total(in_B, 2), name="squares")

    def members(slot_range):
        return [gp.quicksum(v * holds[s, v] for v in values) for s in slot_range]

    return model, {"A": members(in_A), "B": members(in_B)}
