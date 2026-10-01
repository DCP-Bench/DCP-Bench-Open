# Resource-constrained project scheduling (RCPSP): schedule jobs with given durations so that
# precedences hold and no resource is ever used beyond its capacity, minimising the project end.
import cpmpy as cp


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]               # needs[j][r] = units of resource r used by job j
    capacities = instance["resource_capacities_data"]     # capacities[r] = units of resource r available
    precedences = instance["successors_link_data"]        # [a, b]: job b starts after job a has finished
    n_jobs = len(durations)
    n_resources = len(capacities)

    # start_time[j] = start of job j. Running every job one after the other is always feasible,
    # so no job needs to start later than the total duration.
    horizon = sum(durations)
    start_time = cp.intvar(0, horizon, shape=n_jobs, name="start_time")

    model = cp.Model()

    # Precedence: job b may only start once job a has finished.
    for a, b in precedences:
        model += start_time[b] >= start_time[a] + durations[a]

    # Resource capacity: at any time the running jobs together need no more of a resource than
    # is available.
    for r in range(n_resources):
        model += cp.Cumulative(start=start_time,
                               duration=durations,
                               end=start_time + durations,
                               demand=[needs[j][r] for j in range(n_jobs)],
                               capacity=capacities[r])

    # Minimise the project end. The jobs are linked so that the last job is a dummy of duration 0
    # that follows all others, so the project ends when the latest job starts.
    model.minimize(cp.max(start_time))

    return model, {"start_time": start_time}
