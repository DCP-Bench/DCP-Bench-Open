from ortools.sat.python import cp_model


def build(instance):
    """Arch friends: work out the order in which Harriet bought four pairs of
    shoes and where she bought each.

    The puzzle states its own four shoes, four stores and clues, so `instance`
    is unused.  Every variable holds a stop number from 1 to 4, so two
    variables being equal means shoe and store coincide at that stop.
    """
    del instance

    n = 4
    model = cp_model.CpModel()
    shoes = [model.new_int_var(1, n, f"shoe{i}") for i in range(n)]
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    store = [model.new_int_var(1, n, f"store{i}") for i in range(n)]
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    model.add_all_different(shoes)
    model.add_all_different(store)
    # 1. Fuchsia flats came from Heels in a Handcart.
    model.add(fuchsiaflats == heelsinahandcart)
    # 2. The stop after the purple pumps was not Tootsies.
    model.add(purplepumps + 1 != tootsies)
    # 3. The Foot Farm was the second stop.
    model.add(footfarm == 2)
    # 4. The suede sandals came two stops after The Shoe Palace.
    model.add(theshoepalace + 2 == suedesandals)

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
