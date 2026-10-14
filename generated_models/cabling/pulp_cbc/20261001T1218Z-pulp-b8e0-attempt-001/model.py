"""Cabling: place n one-unit devices in the slots of a rack, one device per slot,
so that the total length of the cables joining them is as short as possible.

Each entry of cable_struct names two devices and the number of cables between
them. A cable's length is the distance between the slots of its two devices, so
the total is the sum over entries of (number of cables) * |slot of a - slot of b|.
The output is that smallest total length.
"""
import pulp


def build(instance):
    n = instance["n"]                    # number of devices = number of rack slots
    devices = instance["devices"]        # device names
    cable_struct = instance["cable_struct"]  # entries [device, device, number of cables]

    index = {name: i for i, name in enumerate(devices)}
    cables = [(index[a], index[b], count) for a, b, count in cable_struct]

    problem = pulp.LpProblem("cabling", pulp.LpMinimize)

    # in_slot[d][p] = 1 if device d is placed in slot p
    in_slot = [[pulp.LpVariable(f"in_slot_{d}_{p}", cat="Binary") for p in range(n)]
               for d in range(n)]

    # all devices have distinct slots: each device takes one slot, each slot holds one device
    for d in range(n):
        problem += pulp.lpSum(in_slot[d]) == 1
    for p in range(n):
        problem += pulp.lpSum(in_slot[d][p] for d in range(n)) == 1

    # x[d] = the slot of device d
    x = [pulp.LpVariable(f"x_{d}", 0, n - 1, cat="Integer") for d in range(n)]
    for d in range(n):
        problem += x[d] == pulp.lpSum(p * in_slot[d][p] for p in range(n))

    # Mirroring the rack (slot p becomes n-1-p) keeps every cable length, so the
    # smallest total is the same when device 0 is in the lower half. This only cuts
    # mirror-image placements; the declared output, the smallest total length, is
    # unchanged.
    if n > 0:
        problem += 2 * x[0] <= n - 1

    # length[i] = distance between the slots of the two devices of cable entry i;
    # minimisation pushes it down to the absolute difference, so two lower bounds suffice
    length = [pulp.LpVariable(f"length_{i}", 0, n - 1) for i in range(len(cables))]
    for i, (a, b, count) in enumerate(cables):
        problem += length[i] >= x[a] - x[b]
        problem += length[i] >= x[b] - x[a]

    # final_sum = total cable length (declared output). The longest a cable can be
    # is n - 1 slots, which bounds it.
    final_sum = pulp.LpVariable("final_sum", 0, (n - 1) * sum(count for _, _, count in cables),
                                cat="Integer")
    total = pulp.lpSum(count * length[i] for i, (_, _, count) in enumerate(cables))
    problem += final_sum == total

    # objective: minimise the total cable length
    problem += final_sum

    return problem, {"final_sum": final_sum}
