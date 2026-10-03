"""Thick as thieves: six suspects, at most two guilty; the innocent tell the truth and the
guilty lie. From their statements, find who is guilty.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data.
    model = Model("thick_as_thieves")
    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    guilty = {x: model.binary_var(name=x) for x in names}  # 1 means guilty
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[x] for x in names)

    # The getaway car held at most two, so at most two are guilty.
    model.add_constraint(model.sum(guilty.values()) <= 2)

    # A suspect is guilty exactly when his statement is false.
    # Artie: "It wasn't me." False exactly when Artie is guilty, so it holds whatever Artie is.
    # Bill: "Crackitt was in it." Bill is guilty exactly when Crackitt is not.
    model.add_constraint(bill + crackitt == 1)
    # Crackitt: "No I wasn't." Like Artie's, it holds whatever Crackitt is.
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is
    # guilty and Bill is not: dodgy == crackitt and not bill.
    model.add_constraint(dodgy <= crackitt)
    model.add_constraint(dodgy <= 1 - bill)
    model.add_constraint(dodgy >= crackitt - bill)
    # Edgy: "Nobody did it alone" (more than one is guilty). False exactly when at most one
    # is guilty.
    model.add_equivalence(edgy, model.sum(guilty.values()) <= 1)
    # Fingers: "It was Artie and Dodgy together." False exactly when not both are guilty:
    # fingers == not (artie and dodgy).
    model.add_constraint(fingers + artie >= 1)
    model.add_constraint(fingers + dodgy >= 1)
    model.add_constraint(fingers + artie + dodgy <= 2)

    return model, dict(guilty)
