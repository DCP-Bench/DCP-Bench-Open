# Cabling: put devices one above another in a rack (one device per slot) so
# that the total cable length is as small as possible. A cable joining two
# devices, or several identical cables between them, costs the distance between
# their slots times the number of cables.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # number of devices and rack slots
    devices = instance["devices"]  # device names
    cables = instance["cable_struct"]  # [device a, device b, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    links = [(index[a], index[b], count) for a, b, count in cables]

    m = Model()
    # x[d] = the slot of device d; every device gets its own slot
    x = m.int_vector("x", n, 0, n - 1)
    m &= x.all_different()

    # distance[k] = the distance between the slots of the two devices of cable group k:
    # for every pair of slots p != q it is |p - q|
    distance = []
    for k, (a, b, count) in enumerate(links):
        d = m.int(f"distance_{k}", 1, n - 1)
        for p in range(n):
            for q in range(n):
                if p != q:
                    m &= (~(x[a] == p) | ~(x[b] == q) | (d == abs(p - q)))
        distance.append(d)

    # Minimise the total cable length. A cable group pays its cable count once for every
    # unit of distance above 1 (the distance is at least 1 whatever the slots, which adds a
    # constant), that is when distance >= t holds for t = 2, 3, ...
    for k, (a, b, count) in enumerate(links):
        for t in range(2, n):
            m.obj[count] += ~(distance[k] >= t)

    # final_sum is a declared output: the cable length as a sum of scaled distances
    final_sum = m.sum_var([m.scale(distance[k], links[k][2]) for k in range(len(links))])

    return m, {"final_sum": final_sum}
