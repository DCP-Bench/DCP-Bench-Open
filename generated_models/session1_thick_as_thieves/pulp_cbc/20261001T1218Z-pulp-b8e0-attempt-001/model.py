"""Thick as thieves: six suspects, at most two of them guilty; the innocent tell the truth
and the guilty lie. From their statements, find who is guilty.

The model reports whether each suspect is guilty (1) or not (0).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]

    problem = pulp.LpProblem("thick_as_thieves", pulp.LpMinimize)  # satisfaction

    guilty = {x: pulp.LpVariable(x, cat="Binary") for x in names}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[x] for x in names)
    count = pulp.lpSum(guilty.values())

    # at most two are guilty: the getaway car held two
    problem += count <= 2

    # Each suspect is guilty exactly when their statement is false.
    # Artie: "It wasn't me." and Crackitt: "No I wasn't." are false exactly when the
    # speaker is guilty, so they hold for any choice and add nothing.

    # Bill: "Crackitt was in it up to his neck." Bill is guilty iff Crackitt is not
    problem += bill == 1 - crackitt

    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is
    # guilty and Bill is not, so Dodgy = Crackitt and not Bill
    problem += dodgy <= crackitt
    problem += dodgy <= 1 - bill
    problem += dodgy >= crackitt - bill

    # Edgy: "Nobody did it alone." (more than one is guilty). Edgy is guilty iff at most
    # one is guilty; 6 is the most the count can be
    problem += count <= 1 + 5 * (1 - edgy)
    problem += count >= 2 - 2 * edgy

    # Fingers: "It was Artie and Dodgy together." Fingers is guilty iff not both are
    both = pulp.LpVariable("artie_and_dodgy", cat="Binary")
    problem += both <= artie
    problem += both <= dodgy
    problem += both >= artie + dodgy - 1
    problem += fingers == 1 - both

    return problem, guilty
