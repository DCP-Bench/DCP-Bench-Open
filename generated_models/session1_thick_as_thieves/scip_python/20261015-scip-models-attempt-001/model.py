# Thick as thieves: which of six suspects are guilty, when the innocent tell the truth and the guilty lie.
from pyscipopt import Model, quicksum

NAMES = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def build(instance):
    m = Model("thick_as_thieves")

    # guilty[s] = 1 if suspect s is guilty
    guilty = {s: m.addVar(name=f"guilty_{s}", vtype="B") for s in NAMES}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[s] for s in NAMES)

    # truth[s] = 1 if the statement made by suspect s is true
    truth = {s: m.addVar(name=f"truth_{s}", vtype="B") for s in NAMES}

    # negations of the suspects' guilt, used inside the statements
    not_guilty = {s: m.addVar(name=f"innocent_{s}", vtype="B") for s in NAMES}
    for s in NAMES:
        m.addCons(not_guilty[s] + guilty[s] == 1)
    innocent = not_guilty

    # the getaway car was barely big enough to hold two, so at most two are guilty
    # the robbery had at least one guilty person
    total_guilty = quicksum(guilty[s] for s in NAMES)
    m.addCons(total_guilty <= 2)
    m.addCons(total_guilty >= 1)

    # the innocent ones tell the truth and the guilty ones lie
    for s in NAMES:
        m.addCons(truth[s] + guilty[s] == 1)

    # Artie: "It wasn't me." Artie's statement is "Artie is innocent", so it is
    # true exactly when Artie is innocent. That holds by the rule above, so no
    # extra constraint is needed.

    # Bill: "Crackitt was in it up to his neck." True exactly when Crackitt is guilty.
    m.addCons(truth["bill"] == crackitt)

    # Crackitt: "No I wasn't." Self-referential: true exactly when Crackitt is innocent,
    # which the rule above already gives.

    # Dodgy: "If Crackitt did it, Bill did it with him." True exactly when
    # Crackitt is innocent or Bill is guilty.
    m.addConsOr([innocent["crackitt"], bill], truth["dodgy"])

    # Edgy: "Nobody did it alone." True exactly when the number of guilty ones is
    # not one. With one to two guilty, that means two guilty.
    m.addConsIndicator(total_guilty >= 2, binvar=truth["edgy"])
    m.addConsIndicator(total_guilty <= 1, binvar=truth["edgy"], activeone=False)

    # Fingers: "That's right: it was Artie and Dodgy together." True exactly when
    # the guilty ones are Artie and Dodgy and nobody else.
    m.addConsAnd(
        [artie, dodgy, innocent["bill"], innocent["crackitt"], innocent["edgy"], innocent["fingers"]],
        truth["fingers"],
    )

    outputs = {s: guilty[s] for s in NAMES}
    return m, outputs
