# Thick as thieves: six suspects, at most two of them guilty. The innocent tell
# the truth and the guilty lie in what they said.
from itertools import combinations

from hermax.model import Model

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    m = Model()
    # guilty[name] is true when the suspect took part
    guilty = {name: m.bool(name) for name in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in SUSPECTS)

    # the getaway car held two, so at most two are guilty
    m &= (sum(1 * guilty[name] for name in SUSPECTS) <= 2)

    # A suspect is guilty exactly when what he said is false.
    # Artie: "It wasn't me." and Crackitt: "No I wasn't." Each is guilty exactly when
    # he says something false about himself, which holds for either value, so
    # neither statement restricts anything.
    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    m &= (bill | crackitt)
    m &= (~bill | ~crackitt)
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt
    # is guilty and Bill is not, and then Dodgy is guilty.
    m &= (~dodgy | crackitt)
    m &= (~dodgy | ~bill)
    m &= (dodgy | ~crackitt | bill)
    # Edgy: "Nobody did it alone." False exactly when at most one suspect is guilty.
    # If Edgy is guilty at most one is; if not, at least two are (each suspect has
    # another guilty one beside him).
    for a, b in combinations(SUSPECTS, 2):
        m &= (~edgy | ~guilty[a] | ~guilty[b])
    for name in SUSPECTS:
        others = [guilty[o] for o in SUSPECTS if o != name]
        clause = edgy
        for lit in others:
            clause = clause | lit
        m &= clause
    # Fingers: "That's right: it was Artie and Dodgy together." False exactly when
    # Artie and Dodgy are not both guilty.
    m &= (~fingers | ~artie | ~dodgy)
    m &= (fingers | artie)
    m &= (fingers | dodgy)

    return m, guilty
