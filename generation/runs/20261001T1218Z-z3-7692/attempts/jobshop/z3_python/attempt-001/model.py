# Job shop: jobs are sequences of tasks, each task runs on a given machine for a given time.
# The tasks of a job follow each other in order, a machine runs one task at a time, and a task
# runs without interruption. Minimize the makespan, the time when all jobs are finished.
import z3


def build(instance):
    jobs_data = instance["jobs_data"]  # jobs_data[job][task] = [machine, duration]
    n_jobs = len(jobs_data)
    machines = sorted({task[0] for job in jobs_data for task in job})
    # Upper bound on every time: all the work done one piece after the other.
    max_duration = sum(task[1] for job in jobs_data for task in job)

    # Start and end time of every task of every job (jobs may have different numbers of tasks).
    start = [[z3.Int(f"start_{j}_{t}") for t in range(len(job))] for j, job in enumerate(jobs_data)]
    end = [[z3.Int(f"end_{j}_{t}") for t in range(len(job))] for j, job in enumerate(jobs_data)]
    makespan = z3.Int("makespan")

    solver = z3.Solver()

    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            # Times are between 0 and the total amount of work (the reference's bounds).
            solver.add(start[j][t] >= 0, start[j][t] <= max_duration)
            solver.add(end[j][t] >= 0, end[j][t] <= max_duration)
            # A task runs to completion once started.
            solver.add(end[j][t] == start[j][t] + duration)
            # No task of a job can start before the previous task of that job has ended.
            if t > 0:
                solver.add(start[j][t] >= end[j][t - 1])

    # A machine can only work on one task at a time: for every two tasks on the same
    # machine, one ends before the other starts.
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, task in enumerate(job)
                 if task[0] == machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                (j1, t1), (j2, t2) = tasks[a], tasks[b]
                solver.add(z3.Or(start[j1][t1] >= end[j2][t2], start[j2][t2] >= end[j1][t1]))

    # The makespan is the latest end time of all the tasks.
    last_ends = [end[j][len(job) - 1] for j, job in enumerate(jobs_data)]
    for e in last_ends:
        solver.add(makespan >= e)
    solver.add(z3.Or([makespan == e for e in last_ends]))

    # Implied lower bounds on the makespan: a job needs the sum of its task times, and a
    # machine needs the sum of the times of its tasks.
    for job in jobs_data:
        solver.add(makespan >= sum(task[1] for task in job))
    for machine in machines:
        solver.add(makespan >= sum(task[1] for job in jobs_data for task in job if task[0] == machine))

    # Minimize the makespan.
    return solver, {"makespan": makespan}, ("minimize", makespan)
