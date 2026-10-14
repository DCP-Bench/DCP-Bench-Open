"""Arch friends logic puzzle: Harriet bought four different pairs of shoes (ecru espadrilles,
fuchsia flats, purple pumps, suede sandals) at four different stores (Foot Farm, Heels in a
Handcart, The Shoe Palace, Tootsies), one per stop; find the stop (1..4) of each shoe and each
store from the clues.

The model reports the stop number of every shoe and every store. The puzzle has no instance
data; the clues are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    n = 4  # four stops (puzzle constant)
    stops = range(1, n + 1)
    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    stores = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    model = Model("arch_friends")

    # at[x, s] = 1 when shoe or store x belongs to stop s. Every shoe is bought at a different
    # stop and every store is visited at a different stop.
    at = {(x, s): model.binary_var(name=f"{x}_{s}") for x in shoes + stores for s in stops}
    for group in (shoes, stores):
        for x in group:
            model.add_constraint(model.sum(at[x, s] for s in stops) == 1)
        for s in stops:
            model.add_constraint(model.sum(at[x, s] for x in group) == 1)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    for s in stops:
        model.add_constraint(at["fuchsiaflats", s] == at["heelsinahandcart", s])

    # 2. The store she visited just after buying her purple pumps was not Tootsies.
    for s in stops:
        if s + 1 in stops:
            model.add_constraint(at["purplepumps", s] + at["tootsies", s + 1] <= 1)

    # 3. The Foot Farm was Harriet's second stop.
    model.add_constraint(at["footfarm", 2] == 1)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    for s in stops:
        model.add_constraint(at["suedesandals", s] == (at["theshoepalace", s - 2] if s - 2 in stops else 0))

    return model, {x: model.sum(s * at[x, s] for s in stops) for x in shoes + stores}
