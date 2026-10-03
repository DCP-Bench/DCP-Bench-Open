"""Thick as thieves: six suspects, at most two guilty; the innocent tell the truth and the guilty lie. Who is guilty?"""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: six suspects and a car that holds two.
SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
CAR_SEATS = 2


def build(instance):
    model = gp.Model("session1_thick_as_thieves")

    # guilty[s] = 1 when suspect s is guilty.
    guilty = {s: model.addVar(vtype=GRB.BINARY, name=s) for s in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[s] for s in SUSPECTS)
    total = gp.quicksum(guilty.values())

    # The getaway car held at most two, so at most two are guilty.
    model.addConstr(total <= CAR_SEATS, name="car")

    # A suspect is guilty exactly when his statement is false.

    # Artie: "It wasn't me." It is false exactly when Artie is guilty, so it
    # holds for either value of artie and adds nothing.

    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when
    # Crackitt is not.
    model.addConstr(bill == 1 - crackitt, name="bill_says")

    # Crackitt: "No I wasn't." Like Artie's, it holds for either value.

    # Dodgy: "If Crackitt did it, Bill did it with him." It is false exactly
    # when Crackitt did it and Bill did not: dodgy = crackitt and not bill.
    model.addConstr(dodgy <= crackitt, name="dodgy_says_1")
    model.addConstr(dodgy <= 1 - bill, name="dodgy_says_2")
    model.addConstr(dodgy >= crackitt - bill, name="dodgy_says_3")

    # Edgy: "Nobody did it alone", i.e. more than one is guilty. Edgy is
    # guilty exactly when at most one is.
    model.addConstr((edgy == 1) >> (total <= 1), name="edgy_lies")
    model.addConstr((edgy == 0) >> (total >= 2), name="edgy_true")

    # Fingers: "It was Artie and Dodgy together." Fingers is guilty exactly
    # when not both Artie and Dodgy are.
    both = model.addVar(vtype=GRB.BINARY, name="artie_and_dodgy")
    model.addConstr(both == gp.and_(artie, dodgy), name="both")
    model.addConstr(fingers == 1 - both, name="fingers_says")

    return model, dict(guilty)
