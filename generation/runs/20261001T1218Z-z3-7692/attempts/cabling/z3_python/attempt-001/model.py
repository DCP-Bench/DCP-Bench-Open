# Cabling: place the devices in the slots of a rack, one device per slot, so that
# the total length of all the cables between devices is as short as possible.
import z3


def build(instance):
    n = instance["n"]                        # number of devices (and rack slots)
    devices = instance["devices"]            # device names
    cable_struct = instance["cable_struct"]  # [device, device, number of cables] rows

    # Turn the device names into indices.
    device_map = {name: i for i, name in enumerate(devices)}
    cables = [(device_map[a], device_map[b], num) for a, b, num in cable_struct]

    # x[d] is the rack slot of device d.
    x = [z3.Int(f"x_{d}") for d in range(n)]
    # t[i] is the total length of the cables of row i (cable length = slot distance,
    # times the number of cables between the two devices).
    t = [z3.Int(f"t_{i}") for i in range(len(cables))]
    # final_sum is the total length of all cables.
    final_sum = z3.Int("final_sum")

    solver = z3.Solver()

    for d in range(n):
        solver.add(x[d] >= 0, x[d] <= n - 1)
    # The reference bounds each row's length between 1 and n * n.
    for ti in t:
        solver.add(ti >= 1, ti <= n * n)
    # And the total between 0 and n * n times the number of cables (reference bound).
    solver.add(final_sum >= 0, final_sum <= n * n * sum(c[2] for c in cables))

    # All devices have distinct positions in the rack.
    solver.add(z3.Distinct(x))

    # The cable length of a row is the distance between its two devices in the rack,
    # times the number of cables connecting them.
    for i, (a, b, num) in enumerate(cables):
        solver.add(t[i] == z3.Abs(x[a] - x[b]) * num)

    # The total cable length is the sum of the lengths of all rows.
    solver.add(final_sum == z3.Sum(t))

    # Make the total cable length as short as possible.
    return solver, {"final_sum": final_sum}, ("minimize", final_sum)
