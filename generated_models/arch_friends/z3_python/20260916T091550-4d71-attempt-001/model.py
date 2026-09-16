import z3


def build(instance):
    """Arch friends: the order in which Harriet bought four pairs of shoes and
    where she bought each.

    The puzzle states its own shoes, stores and clues, so it carries no
    instance data.  Every variable holds a stop number from 1 to 4.
    """
    del instance

    n = 4
    shoes = z3.Ints("ecruespadrilles fuchsiaflats purplepumps suedesandals")
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    store = z3.Ints("footfarm heelsinahandcart theshoepalace tootsies")
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    solver = z3.Solver()
    for value in list(shoes) + list(store):
        solver.add(value >= 1, value <= n)
    solver.add(z3.Distinct(shoes))
    solver.add(z3.Distinct(store))

    # 1. Fuchsia flats came from Heels in a Handcart.
    solver.add(fuchsiaflats == heelsinahandcart)
    # 2. The stop after the purple pumps was not Tootsies.
    solver.add(purplepumps + 1 != tootsies)
    # 3. The Foot Farm was the second stop.
    solver.add(footfarm == 2)
    # 4. The suede sandals came two stops after The Shoe Palace.
    solver.add(theshoepalace + 2 == suedesandals)

    return solver, {
        "ecruespadrilles": ecruespadrilles, "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps, "suedesandals": suedesandals,
        "footfarm": footfarm, "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace, "tootsies": tootsies,
    }
