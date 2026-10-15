# Order in which Harriet bought four pairs of shoes, and the store of each purchase (four stops).
from pyscipopt import Model, quicksum

SHOES = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
STORES = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]
# the four stops are numbered 1 to 4, as in the description ("second stop")
STOPS = [1, 2, 3, 4]


def build(instance):
    # The problem has no instance fields: the four shoes, four stores and four stops are fixed.
    m = Model()

    # shoe[a, k] = 1 if shoe a is bought at stop k
    shoe = {(a, k): m.addVar(name=f"shoe_{a}_{k}", vtype="B") for a in SHOES for k in STOPS}
    # store[t, k] = 1 if stop k is at store t
    store = {(t, k): m.addVar(name=f"store_{t}_{k}", vtype="B") for t in STORES for k in STOPS}

    # each shoe is bought at exactly one stop, and each stop is one shoe
    for a in SHOES:
        m.addCons(quicksum(shoe[a, k] for k in STOPS) == 1)
    for k in STOPS:
        m.addCons(quicksum(shoe[a, k] for a in SHOES) == 1)

    # each store is one stop, and each stop is one store
    for t in STORES:
        m.addCons(quicksum(store[t, k] for k in STOPS) == 1)
    for k in STOPS:
        m.addCons(quicksum(store[t, k] for t in STORES) == 1)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart (same stop)
    for k in STOPS:
        m.addCons(shoe["fuchsiaflats", k] == store["heelsinahandcart", k])

    # 2. The store visited just after buying the purple pumps was not Tootsies
    for k in STOPS:
        if k + 1 in STOPS:
            m.addCons(shoe["purplepumps", k] + store["tootsies", k + 1] <= 1)

    # 3. The Foot Farm was Harriet's second stop
    m.addCons(store["footfarm", 2] == 1)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought the suede sandals
    for k in STOPS:
        if k + 2 in STOPS:
            m.addCons(store["theshoepalace", k] <= shoe["suedesandals", k + 2])
        else:
            m.addCons(store["theshoepalace", k] == 0)

    # outputs: the stop number of each shoe and of each store
    outputs = {}
    for a in SHOES:
        outputs[a] = quicksum(k * shoe[a, k] for k in STOPS)
    for t in STORES:
        outputs[t] = quicksum(k * store[t, k] for k in STOPS)

    return m, outputs
