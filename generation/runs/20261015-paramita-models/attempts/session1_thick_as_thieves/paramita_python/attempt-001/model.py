"""Thick as thieves: who is guilty among six suspects.

Six suspects, Artie, Bill, Crackitt, Dodgy, Edgy and Fingers. Innocent suspects
tell the truth; guilty suspects lie. At least four are innocent, and the
getaway car could hold only two, so at most two are guilty and at least one is.
Each suspect's guilt is one Bool; a statement is true exactly when its speaker is innocent.
"""

from paramita.modelling import And, Bool, Iff, Or


def build(instance):
    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    g = {n: Bool(f"guilty_{n}") for n in names}
    gA, gB, gC, gD, gE, gF = (g[n] for n in names)
    guilty_count = sum(g.values())

    cons = []

    # the getaway car was barely big enough to hold two, so at most two are guilty
    cons.append(guilty_count <= 2)
    # at least four of them are innocent, which the car limit above covers
    # the guilty one or ones: at least one suspect is guilty
    cons.append(guilty_count >= 1)

    # Artie: "It wasn't me." The statement is true exactly when Artie is innocent.
    cons.append(Iff(~gA, ~gA))

    # Bill: "Crackitt was in it up to his neck." True exactly when Bill is innocent.
    cons.append(Iff(~gB, gC))

    # Crackitt: "No I wasn't." True exactly when Crackitt is innocent.
    cons.append(Iff(~gC, ~gC))

    # Dodgy: "If Crackitt did it, Bill did it with him." Implication Crackitt -> Bill.
    cons.append(Iff(~gD, Or(~gC, gB)))

    # Edgy: "Nobody did it alone." True when the guilty set is not a single suspect.
    cons.append(Iff(~gE, Or(guilty_count == 0, guilty_count >= 2)))

    # Fingers: "It was Artie and Dodgy together." True when the guilty set is exactly {Artie, Dodgy}.
    exactly_artie_dodgy = And([gA, gD, ~gB, ~gC, ~gE])
    cons.append(Iff(~gF, exactly_artie_dodgy))

    outputs = {n: g[n] for n in names}
    return cons, outputs
