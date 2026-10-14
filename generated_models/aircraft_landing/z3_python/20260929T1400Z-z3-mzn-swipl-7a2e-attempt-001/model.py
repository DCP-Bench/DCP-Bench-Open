# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
import z3


def build(instance):
    earliest = instance["earliest_landing"]  # start of each aircraft's window
    latest = instance["latest_landing"]  # end of each aircraft's window
    target = instance["target_landing"]  # preferred landing time
    penalty_before = instance["penalty_before"]  # cost per time unit landing early
    penalty_after = instance["penalty_after"]  # cost per time unit landing late
    separation = instance["separation_time"]  # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)

    solver = z3.Solver()

    landing_times = [z3.Int(f"landing_{i}") for i in range(n)]
    # how far before / after its target each aircraft lands
    earliness = [z3.Int(f"earliness_{i}") for i in range(n)]
    lateness = [z3.Int(f"lateness_{i}") for i in range(n)]

    for i in range(n):
        # each aircraft lands inside its time window
        solver.add(landing_times[i] >= earliest[i], landing_times[i] <= latest[i])
        # earliness and lateness are non-negative and bounded by the horizon
        solver.add(earliness[i] >= 0, earliness[i] <= horizon, lateness[i] >= 0, lateness[i] <= horizon)
        # the deviation from the target is split into earliness and lateness;
        # the positive penalties make the solver keep one of the two at zero
        solver.add(landing_times[i] - target[i] == lateness[i] - earliness[i])

    # the landing order is fixed as the aircraft index order (as the problem
    # states), so aircraft j lands at least separation[i][j] after aircraft i
    for i in range(n):
        for j in range(i + 1, n):
            solver.add(landing_times[j] - landing_times[i] >= separation[i][j])

    # total penalty for early and late landings, declared as an output and minimised
    total_penalty = z3.Int("total_penalty")
    solver.add(total_penalty == z3.Sum([penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                                        for i in range(n)]))

    return solver, {"landing_times": landing_times, "total_penalty": total_penalty}, ("minimize", total_penalty)
