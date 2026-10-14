# Aircraft landing with a fixed landing order: give every aircraft a landing
# time inside its window so that consecutive landings keep the required
# separation, minimising the penalty for landing before or after the target.
from hermax.model import Model


def build(instance):
    earliest = instance["earliest_landing"]  # start of each aircraft's window
    latest = instance["latest_landing"]  # end of each aircraft's window
    target = instance["target_landing"]  # preferred landing time
    penalty_before = instance["penalty_before"]  # cost per time unit landing early
    penalty_after = instance["penalty_after"]  # cost per time unit landing late
    separation = instance["separation_time"]  # minimum gap between two landings
    n = len(earliest)
    horizon = max(latest)

    m = Model()
    landing_times = m.int_vector("landing_times", n, 0, horizon)
    # how far before / after its target each aircraft lands
    earliness = m.int_vector("earliness", n, 0, horizon)
    lateness = m.int_vector("lateness", n, 0, horizon)

    for i in range(n):
        # each aircraft lands inside its time window
        m &= (landing_times[i] >= earliest[i])
        m &= (landing_times[i] <= latest[i])
        # the deviation from the target is split into earliness and lateness; the
        # positive penalties make the solver keep one of the two at zero
        m &= (landing_times[i] - lateness[i] + earliness[i] == target[i])

    # the landing order is fixed as the aircraft index order (as the problem
    # states), so aircraft j lands at least separation[i][j] after aircraft i
    for i in range(n):
        for j in range(i + 1, n):
            m &= (landing_times[j] - landing_times[i] >= separation[i][j])

    # Minimise the total penalty: each time unit of earliness or lateness pays its
    # penalty exactly when earliness (lateness) >= k holds, the soft clause is the negation.
    for i in range(n):
        for k in range(1, horizon + 1):
            m.obj[penalty_before[i]] += ~(earliness[i] >= k)
            m.obj[penalty_after[i]] += ~(lateness[i] >= k)

    # total_penalty is a declared output, so it is tied to the same sum; it is a sum
    # of scaled integers, which hermax builds from narrow partial sums
    total_penalty = m.sum_var([m.scale(earliness[i], penalty_before[i]) for i in range(n)]
                              + [m.scale(lateness[i], penalty_after[i]) for i in range(n)])

    return m, {"landing_times": landing_times, "total_penalty": total_penalty}
