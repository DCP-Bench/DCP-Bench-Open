# Arch friends: Harriet bought four pairs of shoes at four stores, one pair per stop.
# Find the order of the stops (1 to 4) for each shoe and for each store.
# Each stop has one shoe and one store, and the stop number of a shoe and of its store is the same.
# sh[shoe][p] = 1 if the pair of this shoe was bought at stop p; st[store][p] likewise for stores.
from paramita.modelling import Bool

SHOES = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
STORES = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]
STOPS = [1, 2, 3, 4]


def build(instance):
    sh = {s: {p: Bool(f"shoe_{s}_{p}") for p in STOPS} for s in SHOES}
    st = {t: {p: Bool(f"store_{t}_{p}") for p in STOPS} for t in STORES}

    def stop(oh):
        # stop number as an integer expression
        return sum(p * oh[p] for p in STOPS)

    cons = []

    # each shoe is bought at exactly one stop, and each stop has exactly one shoe
    for s in SHOES:
        cons.append(sum(sh[s].values()) == 1)
    for p in STOPS:
        cons.append(sum(sh[s][p] for s in SHOES) == 1)

    # each store is visited at exactly one stop, and each stop has exactly one store
    for t in STORES:
        cons.append(sum(st[t].values()) == 1)
    for p in STOPS:
        cons.append(sum(st[t][p] for t in STORES) == 1)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart (same stop)
    cons.append(stop(sh["fuchsiaflats"]) == stop(st["heelsinahandcart"]))

    # 2. The store visited just after buying her purple pumps was not Tootsies
    for k in STOPS[:-1]:
        cons.append(~(sh["purplepumps"][k] & st["tootsies"][k + 1]))

    # 3. The Foot Farm was Harriet's second stop
    cons.append(st["footfarm"][2])

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    cons.append(stop(st["theshoepalace"]) + 2 == stop(sh["suedesandals"]))

    outputs = {}
    for s in SHOES:
        outputs[s] = stop(sh[s])
    for t in STORES:
        outputs[t] = stop(st[t])

    return cons, outputs
