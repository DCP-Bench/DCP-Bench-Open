# Cabling: place n 1U devices in the slots of a rack, one device per slot,
# so that the sum of all cable lengths is as short as possible. A cable's length
# is the number of slots between its two devices.
from paramita.modelling import Bool, If, And


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    index = {name: i for i, name in enumerate(devices)}
    cables = instance["cable_struct"]

    # place[d][k] is true when device d sits in slot k (one-hot)
    place = [[Bool(f"place_{d}_{k}") for k in range(n)] for d in range(n)]
    cons = []

    # every device sits in exactly one slot
    for d in range(n):
        cons.append(sum(place[d]) == 1)
    # every slot holds exactly one device
    for k in range(n):
        cons.append(sum(place[d][k] for d in range(n)) == 1)

    # each cable entry [a, b, count] adds count cables between devices a and b;
    # its length is the slot distance |k - l| between them
    total = 0
    for c, (a_name, b_name, count) in enumerate(cables):
        a, b = index[a_name], index[b_name]
        # dist[j] is true when the two devices of this cable are j slots apart
        dist = [Bool(f"dist_{c}_{j}") for j in range(n)]
        cons.append(sum(dist) == 1)
        # if device a is in slot k and device b in slot l, their distance is |k - l|
        for k in range(n):
            for l in range(n):
                cons.append(If(And(place[a][k], place[b][l]), dist[abs(k - l)]))
        # sum of all cable lengths: count cables, each of length j
        total = total + sum(count * j * dist[j] for j in range(n))

    # sum of all cable lengths (the objective, and the output final_sum)
    final_sum = total

    return cons, {"final_sum": final_sum}, ("minimize", final_sum)
