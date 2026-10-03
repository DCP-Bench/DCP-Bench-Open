# Arch friends: Harriet bought four kinds of shoes at four different stores, one pair
# per stop. Find at which stop (1 to 4) she bought each kind of shoe and visited each store.
from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 4  # four shoes, four stores, four stops

    m = Model()
    # the stop at which each kind of shoe was bought
    ecruespadrilles = m.int("ecruespadrilles", 1, n)
    fuchsiaflats = m.int("fuchsiaflats", 1, n)
    purplepumps = m.int("purplepumps", 1, n)
    suedesandals = m.int("suedesandals", 1, n)
    # the stop at which each store was visited
    footfarm = m.int("footfarm", 1, n)
    heelsinahandcart = m.int("heelsinahandcart", 1, n)
    theshoepalace = m.int("theshoepalace", 1, n)
    tootsies = m.int("tootsies", 1, n)

    # each pair of shoes was bought at a different stop, and each store visited at a different stop
    m &= m.vector([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]).all_different()
    m &= m.vector([footfarm, heelsinahandcart, theshoepalace, tootsies]).all_different()

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    m &= (fuchsiaflats == heelsinahandcart)

    # 2. The store she visited just after buying her purple pumps was not Tootsies:
    #    if the pumps were bought at stop v, Tootsies was not stop v + 1.
    for v in range(1, n):
        m &= (~(purplepumps == v) | (tootsies != v + 1))

    # 3. The Foot Farm was Harriet's second stop.
    m &= (footfarm == 2)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    m &= (theshoepalace + 2 == suedesandals)

    return m, {
        "ecruespadrilles": ecruespadrilles,
        "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "footfarm": footfarm,
        "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }
