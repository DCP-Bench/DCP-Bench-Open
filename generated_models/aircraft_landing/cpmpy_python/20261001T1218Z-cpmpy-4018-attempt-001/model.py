# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
import cpmpy as cp


def build(instance):
    earliest = instance["earliest_landing"]        # start of each aircraft's window
    latest = instance["latest_landing"]            # end of each aircraft's window
    target = instance["target_landing"]            # preferred landing time
    penalty_before = instance["penalty_before"]    # cost per time unit landing early
    penalty_after = instance["penalty_after"]      # cost per time unit landing late
    separation = instance["separation_time"]       # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)  # no aircraft can land after the latest window end

    landing_times = cp.intvar(0, horizon, shape=n, name="landing_times")
    # How far before / after its target each aircraft lands.
    earliness = cp.intvar(0, horizon, shape=n, name="earliness")
    lateness = cp.intvar(0, horizon, shape=n, name="lateness")

    # Total penalty for early and late landings, bounded by the largest possible deviation.
    total_penalty = cp.intvar(0, horizon * (sum(penalty_before) + sum(penalty_after)), name="total_penalty")

    model = cp.Model()

    for i in range(n):
        # Each aircraft lands inside its time window.
        model += landing_times[i] >= earliest[i]
        model += landing_times[i] <= latest[i]
        # The deviation from the target is split into earliness and lateness; the positive
        # penalties make the solver keep one of the two at zero.
        model += (landing_times[i] - target[i]) == (lateness[i] - earliness[i])

    # The landing order is fixed as the aircraft index order (as the problem states), so
    # aircraft j lands at least separation[i][j] after aircraft i.
    for i in range(n):
        for j in range(i + 1, n):
            model += landing_times[j] - landing_times[i] >= separation[i][j]

    # The total penalty is the penalty-weighted earliness plus lateness of all aircraft.
    model += total_penalty == cp.sum([penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                                      for i in range(n)])

    # Minimise the total penalty.
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}
