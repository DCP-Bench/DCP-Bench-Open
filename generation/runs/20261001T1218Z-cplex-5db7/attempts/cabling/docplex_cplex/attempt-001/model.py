"""Cabling: place devices in a rack, one per position, so that the total cable length is as
short as possible.

Some pairs of devices are joined by several cables. A cable between two devices is as long
as the distance between their positions in the rack. The model finds the least total length.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]                      # number of devices, and of rack positions
    devices = instance["devices"]          # names of the devices
    cable_struct = instance["cable_struct"]  # rows [device, device, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    cables = [(index[a], index[b], count) for a, b, count in cable_struct]

    model = Model("cabling")

    # at[d, p] is 1 when device d sits in rack position p.
    at = model.binary_var_matrix(range(n), range(n), name="at")

    # Every device has exactly one position and every position holds exactly one device
    # (all devices have distinct positions).
    for d in range(n):
        model.add_constraint(model.sum(at[d, p] for p in range(n)) == 1)
    for p in range(n):
        model.add_constraint(model.sum(at[d, p] for d in range(n)) == 1)

    # position[d] is the rack position of device d.
    position = [model.sum(p * at[d, p] for p in range(n)) for d in range(n)]

    # length[k] is the length of one cable of the k-th pair: the distance between the two
    # positions. It is bounded below by both differences. Only the lengths' sum is
    # minimized and every number of cables is positive, so the minimum takes each length down
    # to the larger of the two differences, which is the distance.
    length = [model.integer_var(0, n - 1, name=f"length_{k}") for k in range(len(cables))]
    for k, (a, b, count) in enumerate(cables):
        model.add_constraint(length[k] >= position[a] - position[b])
        model.add_constraint(length[k] >= position[b] - position[a])

    # The sum of all cable lengths: each pair's distance times its number of cables.
    final_sum = model.sum(count * length[k] for k, (a, b, count) in enumerate(cables))

    # Objective: minimize the total cable length.
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}
