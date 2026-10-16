# Cabling: place n 1U devices in the slots of a rack, one device per slot,
# so that the sum of all cable lengths is as short as possible. A cable's length
# is the number of slots between its two devices.
from paramita.modelling import Bool, If


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

    # slot of device d as an integer expression
    pos = [sum(k * place[d][k] for k in range(n)) for d in range(n)]

    # each cable entry [a, b, count] adds count cables between devices a and b.
    # The length t of one such cable is an integer in unary: t >= m + 1 is ge[m].
    # The distance is at most n - 1 slots.
    total = 0
    for c, (a_name, b_name, count) in enumerate(cables):
        a, b = index[a_name], index[b_name]
        ge = [Bool(f"len_{c}_ge_{m + 1}") for m in range(n - 1)]
        for m in range(n - 2):
            cons.append(If(ge[m + 1], ge[m]))
        t = sum(ge)
        # the length is at least the slot difference in both directions;
        # minimising the total pushes each length down to the exact distance
        cons.append(pos[a] - pos[b] <= t)
        cons.append(pos[b] - pos[a] <= t)
        # sum of all cable lengths: count cables, each of length t
        total = total + count * t

    # sum of all cable lengths (the objective, and the output final_sum)
    final_sum = total

    return cons, {"final_sum": final_sum}, ("minimize", final_sum)
