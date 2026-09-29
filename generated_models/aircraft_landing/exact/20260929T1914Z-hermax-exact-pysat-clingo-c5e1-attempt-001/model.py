# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
from exact import Exact


def build(instance):
    earliest = instance["earliest_landing"]  # start of each aircraft's window
    latest = instance["latest_landing"]  # end of each aircraft's window
    target = instance["target_landing"]  # preferred landing time
    penalty_before = instance["penalty_before"]  # cost per time unit landing early
    penalty_after = instance["penalty_after"]  # cost per time unit landing late
    separation = instance["separation_time"]  # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)

    solver = Exact()
    landing_times = [f"landing_{i}" for i in range(n)]
    earliness = [f"earliness_{i}" for i in range(n)]
    lateness = [f"lateness_{i}" for i in range(n)]
    for i in range(n):
        # each aircraft lands inside its time window
        solver.addVariable(landing_times[i], earliest[i], latest[i])
        solver.addVariable(earliness[i], 0, horizon)
        solver.addVariable(lateness[i], 0, horizon)
        # the deviation from the target is split into earliness and lateness; the
        # positive penalties make the solver keep one of the two at zero
        solver.addConstraint([(1, landing_times[i]), (-1, lateness[i]), (1, earliness[i])],
                             True, target[i], True, target[i])

    # the landing order is fixed as the aircraft index order (as the problem
    # states), so aircraft j lands at least separation[i][j] after aircraft i
    for i in range(n):
        for j in range(i + 1, n):
            solver.addConstraint([(1, landing_times[j]), (-1, landing_times[i])], True, separation[i][j])

    # total_penalty is a declared output and the quantity to minimise
    total_penalty = "total_penalty"
    solver.addVariable(total_penalty, 0, horizon * (sum(penalty_before) + sum(penalty_after)))
    terms = [(penalty_before[i], earliness[i]) for i in range(n)] + [(penalty_after[i], lateness[i]) for i in range(n)]
    solver.addConstraint(terms + [(-1, total_penalty)], True, 0, True, 0)

    return solver, {"landing_times": landing_times, "total_penalty": total_penalty}, ("minimize", terms)
