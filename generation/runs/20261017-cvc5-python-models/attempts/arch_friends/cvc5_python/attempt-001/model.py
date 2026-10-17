# Harriet's four shoe purchases (ecru espadrilles, fuchsia flats, purple pumps,
# suede sandals) and the four stores she bought them at (Foot Farm, Heels in a
# Handcart, The Shoe Palace, Tootsies). Each output is the stop number (1 to 4)
# of that shoe or store; the same number means the same shoe or store.
import cvc5.pythonic as cz


def build(instance):
    ecru, fuchsia, purple, suede, foot, heels, palace, tootsies = cz.Ints(
        "ecruespadrilles fuchsiaflats purplepumps suedesandals "
        "footfarm heelsinahandcart theshoepalace tootsies"
    )
    shoes = [ecru, fuchsia, purple, suede]
    stores = [foot, heels, palace, tootsies]
    constraints = []

    # the stops are the numbers 1 to 4, and each shoe and each store has its own stop
    for v in shoes + stores:
        constraints += [v >= 1, v <= 4]
    constraints += [cz.Distinct(shoes), cz.Distinct(stores)]

    # Harriet bought fuchsia flats at Heels in a Handcart
    constraints.append(fuchsia == heels)

    # the store she visited just after buying her purple pumps was not Tootsies
    constraints.append(tootsies != purple + 1)

    # The Foot Farm was Harriet's second stop
    constraints.append(foot == 2)

    # two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    constraints.append(suede == palace + 2)

    outputs = {
        "ecruespadrilles": ecru,
        "fuchsiaflats": fuchsia,
        "purplepumps": purple,
        "suedesandals": suede,
        "footfarm": foot,
        "heelsinahandcart": heels,
        "theshoepalace": palace,
        "tootsies": tootsies,
    }
    return constraints, outputs
