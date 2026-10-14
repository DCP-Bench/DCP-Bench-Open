# Arch friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple pumps,
# suede sandals) at four different stores (Foot Farm, Heels in a Handcart, The Shoe Palace,
# Tootsies), one per stop. Find the stop at which each pair was bought and each store was visited.
from exact import Exact


def build(instance):
    # This problem has no instance data. There are four stops, numbered 1 to 4.
    n = 4

    solver = Exact()

    # shoes[i] / store[i] = the stop (1..4) at which that pair of shoes was bought / that store
    # was visited
    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    store = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    # at_stop[name][s - 1] = 1 when variable `name` equals stop s
    at_stop = {}
    for group in (shoes, store):
        for name in group:
            solver.addVariable(name, 1, n)
            at_stop[name] = [f"{name}_at_{s}" for s in range(1, n + 1)]
            for indicator in at_stop[name]:
                solver.addVariable(indicator, 0, 1)
            # the variable takes exactly one stop as its value
            solver.addConstraint([(1, x) for x in at_stop[name]], True, 1, True, 1)
            solver.addConstraint([(s, at_stop[name][s - 1]) for s in range(1, n + 1)]
                                 + [(-1, name)], True, 0, True, 0)
        # all different: each stop is used exactly once within the group
        for s in range(n):
            solver.addConstraint([(1, at_stop[name][s]) for name in group], True, 1, True, 1)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    solver.addConstraint([(1, "fuchsiaflats"), (-1, "heelsinahandcart")], True, 0, True, 0)

    # 2. The store she visited just after buying her purple pumps was not Tootsies:
    #    purplepumps + 1 != tootsies
    for s in range(1, n):
        solver.addConstraint([(1, at_stop["purplepumps"][s - 1]), (1, at_stop["tootsies"][s])],
                             False, 0, True, 1)

    # 3. The Foot Farm was Harriet's second stop.
    solver.addConstraint([(1, "footfarm")], True, 2, True, 2)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    solver.addConstraint([(1, "theshoepalace"), (-1, "suedesandals")], True, -2, True, -2)

    return solver, {name: name for name in shoes + store}
