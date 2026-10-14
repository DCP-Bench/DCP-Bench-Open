"""Circular table: three card players X, Y, Z of different nationality pass cards to their right; find each one's nationality."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: three seats 0, 1, 2 (1 is right of 0, 2 right
    # of 1, 0 right of 2) and the two clues are the puzzle's own, mirrored from the reference.
    n = 3
    seats = range(n)
    people = ["x", "y", "z", "american", "english", "french"]

    model = gp.Model("circular_table")

    # at[p, s] is 1 when person (or nationality) p sits on seat s.
    at = model.addVars(people, seats, vtype=GRB.BINARY, name="at")
    for p in people:
        model.addConstr(at.sum(p, "*") == 1, name=f"one_seat[{p}]")

    # The three players sit on different seats, and so do the three nationalities.
    for group in (people[:3], people[3:]):
        for s in seats:
            model.addConstr(gp.quicksum(at[p, s] for p in group) == 1)

    # a is right of b: a sits on seat (b + 1) mod 3.
    def right_to(a, b):
        for s in seats:
            model.addConstr(at[a, (s + 1) % n] == at[b, s], name=f"right[{a},{b},{s}]")

    # Y passed three hearts to the American, who sits on Y's right.
    right_to("american", "y")
    # X passed cards to the person who passed theirs to the Frenchwoman: X is right of her.
    right_to("x", "french")

    return model, {p: gp.quicksum(s * at[p, s] for s in seats) for p in people}
