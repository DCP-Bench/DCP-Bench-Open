# Aircraft landing: schedule the landing time of each aircraft on a single runway,
# in the fixed landing sequence given by the instance (aircraft index order),
# minimizing the total penalty for landing earlier or later than the target time,
# within each aircraft's time window and with the minimum separation between
# every pair of landings (i before j) respected.
#
# Each landing time is an integer in binary: earliest_landing[i] plus a sum of
# powers of two over the bits time_bits[i]. The penalty is linear in two binary
# deviations per aircraft: early[i] >= target - landing and late[i] >= landing - target.
# Minimizing penalty_before * early + penalty_after * late gives the exact penalty.
# Binary is used because the windows are wide (hundreds of time steps) and an
# order or one-hot encoding of the time, summed into the objective, ran out of
# memory or crashed the runner when the optimum is fixed.

from paramita.modelling import Bool


def binary_value(name, bits):
    # integer expression sum(2^k * bit_k) over the given bit names
    return sum((1 << k) * Bool(f"{name}_{k}") for k in range(bits))


def bit_count(max_value):
    # number of bits for values 0 .. max_value (0 when max_value is 0)
    return max(max_value, 0).bit_length()


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    pen_before = instance["penalty_before"]
    pen_after = instance["penalty_after"]
    sep = instance["separation_time"]
    n = len(target)

    cons = []
    landing = []
    penalty = []

    for i in range(n):
        # Each aircraft has a specified time window (earliest and latest possible landing time):
        # landing time = earliest + offset, with offset in 0 .. latest - earliest.
        width = latest[i] - earliest[i]
        time_bits = bit_count(width)
        offset = binary_value(f"land_{i}", time_bits)
        landing.append(earliest[i] + offset)
        if (1 << time_bits) - 1 > width:
            cons.append(offset <= width)

        # Penalties are incurred for landing earlier than the target (early amount)
        # or later than the target (late amount).
        early_max = max(0, target[i] - earliest[i])
        if early_max > 0:
            early = binary_value(f"early_{i}", bit_count(early_max))
            cons.append(early >= target[i] - landing[i])
        else:
            early = 0
        late_max = max(0, latest[i] - target[i])
        if late_max > 0:
            late = binary_value(f"late_{i}", bit_count(late_max))
            cons.append(late >= landing[i] - target[i])
        else:
            late = 0
        penalty.append(pen_before[i] * early + pen_after[i] * late)

    # A minimum separation time between the landings of any two aircraft must be respected.
    # The sequence is fixed to the index order, so only the pairs i < j are constrained.
    for i in range(n):
        for j in range(i + 1, n):
            cons.append(landing[j] >= landing[i] + sep[i][j])

    # Objective: minimize the total penalty over all aircraft.
    total = sum(penalty)

    return cons, {"landing_times": landing, "total_penalty": total}, ("minimize", total)
