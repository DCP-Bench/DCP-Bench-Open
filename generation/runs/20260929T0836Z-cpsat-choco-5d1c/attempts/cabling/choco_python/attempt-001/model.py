# Cabling: put devices one above another in a rack (one device per slot) so
# that the total cable length is as small as possible. A cable joining two
# devices, or several identical cables between them, costs the distance between
# their slots times the number of cables.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # number of devices and rack slots
    devices = instance["devices"]  # device names
    cables = instance["cable_struct"]  # [device a, device b, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    links = [(index[a], index[b], count) for a, b, count in cables]

    model = Model()

    # x[d] = the slot of device d; every device gets its own slot
    x = [model.intvar(0, n - 1, name=f"x_{d}") for d in range(n)]
    model.all_different(x).post()

    # each group of cables is as long as the distance between its two devices times the count
    distances = []
    for k, (a, b, count) in enumerate(links):
        distance = model.intvar(1, n - 1, name=f"distance_{k}")
        model.distance(x[a], x[b], "=", distance).post()
        distances.append(distance)

    # total cable length, to be minimised (its range is the reference's declared bound)
    final_sum = model.intvar(0, n * n * sum(count for _, _, count in links), name="final_sum")
    model.scalar(distances, [count for _, _, count in links], "=", final_sum).post()

    return model, {"final_sum": final_sum}, ("minimize", final_sum)
