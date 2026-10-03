"""Aircraft landing: choose the landing time of each aircraft on a single runway so that the
total penalty for landing off target is as small as possible.

Each aircraft has a time window and a target landing time, with a penalty per unit of time
for landing before or after the target. Landings follow the aircraft's index order, with a
minimum separation time between the landings of any two aircraft.
"""
from docplex.mp.model import Model


def build(instance):
    earliest = instance["earliest_landing"]    # earliest landing time of each aircraft
    latest = instance["latest_landing"]        # latest landing time of each aircraft
    target = instance["target_landing"]        # target landing time of each aircraft
    penalty_after = instance["penalty_after"]  # penalty per unit of time landing after the target
    penalty_before = instance["penalty_before"]  # penalty per unit of time landing before the target
    separation = instance["separation_time"]   # separation[i][j]: least time between landings i and j

    n = len(earliest)
    horizon = max(latest)  # no aircraft lands after the latest of the latest landing times

    model = Model("aircraft_landing")

    # landing_times[i] is the landing time of aircraft i. Its bounds are the time window of
    # aircraft i.
    landing_times = [model.integer_var(earliest[i], latest[i], name=f"landing_{i}") for i in range(n)]

    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands.
    earliness = [model.integer_var(0, horizon, name=f"earliness_{i}") for i in range(n)]
    lateness = [model.integer_var(0, horizon, name=f"lateness_{i}") for i in range(n)]

    # The landing time differs from the target by lateness minus earliness.
    for i in range(n):
        model.add_constraint(landing_times[i] - target[i] == lateness[i] - earliness[i])

    # Aircraft land in index order: aircraft j lands at least separation[i][j] after aircraft i,
    # for every i before j.
    for i in range(n):
        for j in range(i + 1, n):
            model.add_constraint(landing_times[j] - landing_times[i] >= separation[i][j])

    # Objective: the total penalty for landing before or after the target.
    total_penalty = model.sum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                              for i in range(n))
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}
