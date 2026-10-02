"""Aircraft landing: choose a landing time for each aircraft on a single runway
so that the total penalty for landing away from the target time is smallest.

The aircraft land in the given order (aircraft i before aircraft j for i < j).
Each has a time window and a target time; landing early or late costs a penalty
per unit of time. Consecutive landings keep a minimum separation time.
"""
import pulp


def build(instance):
    earliest = instance["earliest_landing"]   # start of each aircraft's time window
    latest = instance["latest_landing"]       # end of each aircraft's time window
    target = instance["target_landing"]       # preferred landing time of each aircraft
    penalty_after = instance["penalty_after"]    # cost per unit of time landing after the target
    penalty_before = instance["penalty_before"]  # cost per unit of time landing before the target
    separation = instance["separation_time"]  # separation[i][j]: least gap between i and j landing

    n = len(earliest)

    problem = pulp.LpProblem("aircraft_landing", pulp.LpMinimize)

    # landing_times[i] = time at which aircraft i lands (declared output); the
    # time window bounds it
    landing_times = [pulp.LpVariable(f"landing_{i}", earliest[i], latest[i], cat="Integer")
                     for i in range(n)]

    # earliness[i] / lateness[i] = how long before / after its target aircraft i lands
    earliness = [pulp.LpVariable(f"earliness_{i}", 0, cat="Integer") for i in range(n)]
    lateness = [pulp.LpVariable(f"lateness_{i}", 0, cat="Integer") for i in range(n)]

    # total penalty of the schedule
    penalty = pulp.lpSum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                         for i in range(n))

    # total_penalty (declared output) equals the penalty. Its bound comes from the
    # time windows: aircraft i lands at most target - earliest early or latest -
    # target late, whichever costs more.
    bound = sum(max(penalty_before[i] * max(0, target[i] - earliest[i]),
                    penalty_after[i] * max(0, latest[i] - target[i])) for i in range(n))
    total_penalty = pulp.LpVariable("total_penalty", 0, bound, cat="Integer")
    problem += total_penalty == penalty

    # objective: minimise the total penalty
    problem += penalty

    # the distance from the target is lateness minus earliness; the objective keeps
    # only one of the two non-zero
    for i in range(n):
        problem += landing_times[i] - target[i] == lateness[i] - earliness[i]

    # the aircraft land in the given order, at least the separation time apart
    for i in range(n):
        for j in range(i + 1, n):
            problem += landing_times[j] - landing_times[i] >= separation[i][j]

    return problem, {"landing_times": landing_times, "total_penalty": total_penalty}
