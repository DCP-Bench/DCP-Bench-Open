# Cabling: put devices one above another in a rack (one device per slot) so
# that the total cable length is as small as possible. A cable joining two
# devices, or several identical cables between them, costs the distance between
# their slots times the number of cables.
import cpmpy as cp


def build(instance):
    n = instance["n"]                  # number of devices and rack slots
    devices = instance["devices"]      # device names
    cables = instance["cable_struct"]  # [device a, device b, number of cables]

    # Cables name devices by their label; turn each label into the device's index.
    index = {name: i for i, name in enumerate(devices)}
    links = [(index[a], index[b], count) for a, b, count in cables]

    # x[d] = the rack slot of device d
    x = cp.intvar(0, n - 1, shape=n, name="x")
    # t[k] = total length of the cables of link k
    t = cp.intvar(1, n * n, shape=len(links), name="t")
    # Total cable length, to be minimised. Its range is the largest possible distance (n - 1 < n)
    # times the number of cables of every link.
    final_sum = cp.intvar(0, n * n * sum(count for _, _, count in links), name="final_sum")

    model = cp.Model()

    # Every device gets its own slot in the rack.
    model += cp.AllDifferent(x)

    # The cables of a link are as long as the distance between its two devices times their number.
    for k, (a, b, count) in enumerate(links):
        model += t[k] == cp.abs(x[a] - x[b]) * count

    # The total cable length is the sum over all links.
    model += final_sum == cp.sum(t)

    # Make the total cable length as small as possible.
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}
