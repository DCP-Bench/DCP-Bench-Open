# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
from ortools.sat.python import cp_model


def build(instance):
    earliest = instance["earliest_landing"]  # start of each aircraft's window
    latest = instance["latest_landing"]  # end of each aircraft's window
    target = instance["target_landing"]  # preferred landing time
    penalty_before = instance["penalty_before"]  # cost per time unit landing early
    penalty_after = instance["penalty_after"]  # cost per time unit landing late
    separation = instance["separation_time"]  # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)

    model = cp_model.CpModel()

    landing_times = [model.new_int_var(0, horizon, f"landing_{i}") for i in range(n)]
    # how far before / after its target each aircraft lands
    earliness = [model.new_int_var(0, horizon, f"earliness_{i}") for i in range(n)]
    lateness = [model.new_int_var(0, horizon, f"lateness_{i}") for i in range(n)]

    for i in range(n):
        # each aircraft lands inside its time window
        model.add(landing_times[i] >= earliest[i])
        model.add(landing_times[i] <= latest[i])
        # the deviation from the target is split into earliness and lateness;
        # the positive penalties make the solver keep one of the two at zero
        model.add(landing_times[i] - target[i] == lateness[i] - earliness[i])

    # the landing order is fixed as the aircraft index order (as the problem
    # states), so aircraft j lands at least separation[i][j] after aircraft i
    for i in range(n):
        for j in range(i + 1, n):
            model.add(landing_times[j] - landing_times[i] >= separation[i][j])

    # total penalty for early and late landings
    total_penalty = model.new_int_var(
        0, horizon * (sum(penalty_before) + sum(penalty_after)), "total_penalty"
    )
    model.add(
        total_penalty
        == sum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i] for i in range(n))
    )
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}
