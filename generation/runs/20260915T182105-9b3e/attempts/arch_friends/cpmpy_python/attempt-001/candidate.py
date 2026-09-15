import cpmpy as cp


def build(instance):
    """Arch friends: work out the order in which Harriet bought four pairs of
    shoes and where she bought each.

    The puzzle states its own four shoes, four stores and clues, so `instance`
    is unused.  Every variable holds a stop number from 1 to 4, so two
    variables being equal means shoe and store coincide at that stop.
    """
    del instance

    n = 4
    shoes = cp.intvar(1, n, shape=n, name="shoes")
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    store = cp.intvar(1, n, shape=n, name="store")
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    model = cp.Model(
        cp.AllDifferent(shoes),
        cp.AllDifferent(store),
        # 1. Fuchsia flats came from Heels in a Handcart.
        fuchsiaflats == heelsinahandcart,
        # 2. The stop after the purple pumps was not Tootsies.
        purplepumps + 1 != tootsies,
        # 3. The Foot Farm was the second stop.
        footfarm == 2,
        # 4. The suede sandals came two stops after The Shoe Palace.
        theshoepalace + 2 == suedesandals,
    )

    return model, {
        "ecruespadrilles": ecruespadrilles,
        "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "footfarm": footfarm,
        "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }
