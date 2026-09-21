# Match four pairs of shoes to the four stops they were bought at.
# The clues are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    n = 4
    sat = Sat()
    shoes = sat.ints(n, 1, n)
    store = sat.ints(n, 1, n)
    sat.all_different(shoes)
    sat.all_different(store)

    ecru, fuchsia, purple, suede = shoes
    footfarm, heels, palace, tootsies = store

    # 1. fuchsia flats came from Heels in a Handcart
    sat.same(fuchsia, heels)
    # 2. the stop after the purple pumps was not Tootsies: purple + 1 != tootsies
    for v in range(1, n + 1):
        other = tootsies.literal(v + 1)
        if other is not None:
            sat.clause([-purple.literal(v), -other])
    # 3. the Foot Farm was the second stop
    sat.clause([footfarm.literal(2)])
    # 4. the suede sandals came two stops after The Shoe Palace
    sat.linear_eq([(1, palace), (-1, suede)], -2)

    return sat, {"ecruespadrilles": ecru, "fuchsiaflats": fuchsia,
                 "purplepumps": purple, "suedesandals": suede,
                 "footfarm": footfarm, "heelsinahandcart": heels,
                 "theshoepalace": palace, "tootsies": tootsies}
