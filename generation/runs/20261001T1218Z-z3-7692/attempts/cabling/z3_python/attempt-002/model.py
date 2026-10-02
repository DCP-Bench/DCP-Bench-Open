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

    # at[d][p] is true if device d is placed in rack slot p. Each device takes exactly
    # one slot and each slot holds exactly one device (all devices have distinct
    # positions). Booleans are used instead of an integer slot per device so that
    # cable lengths can be counted without Abs, which Z3 solves slowly.
    at = [[z3.Bool(f"at_{d}_{p}") for p in range(n)] for d in range(n)]
    # before[d][k] is true if device d sits in one of the slots 0..k-1 (before the gap k).
    before = [[z3.Bool(f"before_{d}_{k}") for k in range(n)] for d in range(n)]
    # t[i] is the total length of the cables of row i.
    t = [z3.Int(f"t_{i}") for i in range(len(cables))]
    # final_sum is the total length of all cables.
    final_sum = z3.Int("final_sum")

    solver = z3.Solver()

    # Every device takes exactly one slot, every slot holds exactly one device.
    for d in range(n):
        solver.add(z3.PbEq([(at[d][p], 1) for p in range(n)], 1))
    for p in range(n):
        solver.add(z3.PbEq([(at[d][p], 1) for d in range(n)], 1))

    # before[d][k] says that the slot of d is below k.
    for d in range(n):
        for k in range(n):
            solver.add(before[d][k] == z3.Or([at[d][p] for p in range(k)]))

    # A cable between devices a and b is as long as the distance between their slots,
    # which is the number of gaps k (between slot k - 1 and slot k) that separate them:
    # exactly one of the two devices is before the gap. A row of `num` cables
    # counts each separating gap `num` times.
    for i, (a, b, num) in enumerate(cables):
        gaps = [z3.If(before[a][k] != before[b][k], num, 0) for k in range(1, n)]
        solver.add(t[i] == z3.Sum(gaps))
        # The reference bounds each row's length between 1 and n * n.
        solver.add(t[i] >= 1, t[i] <= n * n)

    # The total is the sum of the lengths of all rows, with the reference's bounds.
    solver.add(final_sum == z3.Sum(t))
    solver.add(final_sum >= 0, final_sum <= n * n * sum(c[2] for c in cables))

    # Make the total cable length as short as possible.
    return solver, {"final_sum": final_sum}, ("minimize", final_sum)
