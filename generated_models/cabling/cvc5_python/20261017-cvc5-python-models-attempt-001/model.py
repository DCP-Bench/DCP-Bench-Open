# Cabling: place n devices in a rack in some order so that the sum of all cable
# lengths is as short as possible. The length of a cable is the distance between
# the positions of its two devices, and some device pairs carry several cables.

import cvc5.pythonic as cz


def build(instance):
    devices = instance["devices"]
    n = instance["n"]
    cables = instance["cable_struct"]

    pos = cz.Ints(" ".join(f"pos_{k}" for k in range(n)))
    if n == 1:
        pos = [pos]

    constraints = []

    # Every device gets a position between 0 and n-1, and no two share one.
    for k in range(n):
        constraints.append(pos[k] >= 0)
        constraints.append(pos[k] <= n - 1)
    constraints.append(cz.Distinct(list(pos)))

    # The total cable length is the sum over all cables of the number of cables
    # times the distance between the two devices they connect.
    terms = []
    for row in cables:
        a = devices.index(row[0])
        b = devices.index(row[1])
        count = int(row[2])
        diff = pos[a] - pos[b]
        dist = cz.If(diff >= 0, diff, -diff)
        terms.append(count * dist)
    total = cz.Sum(terms)

    return constraints, {"final_sum": total}, ("minimize", total)
