# Cabling: put devices one above another in a rack (one device per slot) so
# that the total cable length is as small as possible. A cable joining two
# devices, or several identical cables between them, costs the distance between
# their slots times the number of cables.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # number of devices and rack slots
    devices = instance["devices"]  # device names
    cables = instance["cable_struct"]  # [device a, device b, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    links = [(index[a], index[b], count) for a, b, count in cables]

    model = cp_model.CpModel()

    # x[d] = the slot of device d; every device gets its own slot
    x = [model.new_int_var(0, n - 1, f"x_{d}") for d in range(n)]
    model.add_all_different(x)

    # each group of cables is as long as the distance between its two devices times the count
    lengths = []
    for k, (a, b, count) in enumerate(links):
        distance = model.new_int_var(1, n - 1, f"distance_{k}")
        model.add_abs_equality(distance, x[a] - x[b])
        lengths.append(count * distance)

    # total cable length, to be minimised (its range is the reference's declared bound)
    final_sum = model.new_int_var(0, n * n * sum(count for _, _, count in links), "final_sum")
    model.add(final_sum == sum(lengths))
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}
