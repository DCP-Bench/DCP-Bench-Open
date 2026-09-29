# Resource-constrained project scheduling: start every job so that the
# precedence relations hold and, at every moment, the jobs running together use
# no more of each renewable resource than its capacity, finishing the project
# as early as possible.
from ortools.sat.python import cp_model


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]  # needs[job][resource]
    capacities = instance["resource_capacities_data"]
    precedences = instance["successors_link_data"]  # [a, b]: job b starts after job a has finished
    n_jobs = len(durations)
    horizon = sum(durations)  # a schedule that runs one job at a time is never longer

    model = cp_model.CpModel()

    # start_time[j] = when job j starts
    start_time = [model.new_int_var(0, horizon, f"start_{j}") for j in range(n_jobs)]
    # each job occupies its resource units for its whole duration
    intervals = [model.new_fixed_size_interval_var(start_time[j], durations[j], f"job_{j}") for j in range(n_jobs)]

    # a job can only start when its predecessor has finished
    for a, b in precedences:
        model.add(start_time[b] >= start_time[a] + durations[a])

    # at any time the jobs in progress need no more of a resource than is available
    for r, capacity in enumerate(capacities):
        model.add_cumulative(intervals, [needs[j][r] for j in range(n_jobs)], capacity)

    # the project ends with its latest starting job (the last job is a zero-length dummy), so
    # minimise the largest start time
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, start_time)
    model.minimize(makespan)

    return model, {"start_time": start_time}
