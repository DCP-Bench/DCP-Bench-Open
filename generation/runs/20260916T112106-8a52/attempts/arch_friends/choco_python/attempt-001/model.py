from pychoco.model import Model


def build(instance):
    """Arch friends: the order in which Harriet bought four pairs of shoes and
    where she bought each.  Every variable holds a stop number from 1 to 4.
    """
    del instance

    n = 4
    model = Model()
    shoes = [model.intvar(1, n, name=f"shoe{i}") for i in range(n)]
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    store = [model.intvar(1, n, name=f"store{i}") for i in range(n)]
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    model.all_different(shoes).post()
    model.all_different(store).post()

    # 1. Fuchsia flats came from Heels in a Handcart.
    model.arithm(fuchsiaflats, "=", heelsinahandcart).post()
    # 2. The stop after the purple pumps was not Tootsies.
    model.scalar([purplepumps, tootsies], [1, -1], "!=", -1).post()
    # 3. The Foot Farm was the second stop.
    model.arithm(footfarm, "=", 2).post()
    # 4. The suede sandals came two stops after The Shoe Palace.
    model.scalar([theshoepalace, suedesandals], [1, -1], "=", -2).post()

    return model, {
        "ecruespadrilles": ecruespadrilles, "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps, "suedesandals": suedesandals,
        "footfarm": footfarm, "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace, "tootsies": tootsies,
    }
