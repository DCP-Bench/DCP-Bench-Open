# Thick as thieves: six suspects, at most two of them guilty. The innocent tell
# the truth and the guilty lie in what they said.
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    pool = IDPool()
    # guilty[name] is true when the suspect took part
    guilty = {name: pool.id(name) for name in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in SUSPECTS)
    cnf = CNF()

    # the getaway car held two, so at most two are guilty
    cnf.extend(CardEnc.atmost(lits=list(guilty.values()), bound=2, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # A suspect is guilty exactly when what he said is false.
    # Artie: "It wasn't me." and Crackitt: "No I wasn't." Each is guilty exactly when
    # he says something false about himself, which holds for either value, so
    # neither statement restricts anything.
    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    cnf.append([bill, crackitt])
    cnf.append([-bill, -crackitt])
    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt
    # is guilty and Bill is not, and then Dodgy is guilty.
    cnf.append([-dodgy, crackitt])
    cnf.append([-dodgy, -bill])
    cnf.append([dodgy, -crackitt, bill])
    # Edgy: "Nobody did it alone." False exactly when at most one suspect is guilty.
    # If Edgy is guilty at most one is; if not, at least two are (each suspect has
    # another guilty one beside him).
    for a, b in combinations(guilty.values(), 2):
        cnf.append([-edgy, -a, -b])
    for name in SUSPECTS:
        cnf.append([edgy] + [guilty[other] for other in SUSPECTS if other != name])
    # Fingers: "That's right: it was Artie and Dodgy together." False exactly when
    # Artie and Dodgy are not both guilty.
    cnf.append([-fingers, -artie, -dodgy])
    cnf.append([fingers, artie])
    cnf.append([fingers, dodgy])

    return cnf, guilty
