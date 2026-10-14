# Resource-constrained project scheduling: start every job so that the
# precedence relations hold and, at every moment, the jobs running together use
# no more of each renewable resource than its capacity, finishing the project
# as early as possible.
import z3


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]  # needs[job][resource]
    capacities = instance["resource_capacities_data"]
    precedences = instance["successors_link_data"]  # [a, b]: job b starts after job a has finished
    n_jobs = len(durations)
    horizon = sum(durations)  # a schedule that runs one job at a time is never longer

    solver = z3.Solver()

    # start_time[j] = when job j starts
    start_time = [z3.Int(f"start_{j}") for j in range(n_jobs)]
    for start in start_time:
        solver.add(start >= 0, start <= horizon)

    # a job can only start when its predecessor has finished
    for a, b in precedences:
        solver.add(start_time[b] >= start_time[a] + durations[a])

    # At any time the jobs in progress need no more of a resource than is
    # available. The load only rises when a job starts, so it is enough to check
    # the moment every job starts: the jobs running then (a job runs from its
    # start up to, not including, its start plus its duration) fit the capacity.
    for r, capacity in enumerate(capacities):
        for j in range(n_jobs):
            running = [
                z3.If(z3.And(start_time[i] <= start_time[j], start_time[j] < start_time[i] + durations[i]), needs[i][r], 0)
                for i in range(n_jobs)
                if durations[i] > 0 and needs[i][r] > 0
            ]
            if running:
                solver.add(z3.Sum(running) <= capacity)

    # the project ends with its latest starting job (the last job is a zero-length
    # dummy), so minimise the largest start time
    makespan = z3.Int("makespan")
    solver.add(z3.Or([makespan == start for start in start_time]))
    for start in start_time:
        solver.add(makespan >= start)

    return solver, {"start_time": start_time}, ("minimize", makespan)
