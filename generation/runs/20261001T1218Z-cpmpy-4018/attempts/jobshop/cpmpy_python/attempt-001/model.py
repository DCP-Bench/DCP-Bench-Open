# Job shop: every job is a chain of tasks, each needing one machine for a fixed time. Tasks
# of a job run in order, a machine does one task at a time, and tasks are not interrupted.
# Find the schedule with the shortest makespan, the time at which the last task ends.
import cpmpy as cp


def build(instance):
    jobs_data = instance["jobs_data"]     # jobs_data[j][t] = [machine, duration] of task t of job j

    # A schedule that runs the tasks one after another never exceeds the sum of all durations.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    # start[j][t] is the start time of task t of job j; its end is start + duration.
    start = [[cp.intvar(0, horizon, name=f"start_{j}_{t}") for t in range(len(job))]
             for j, job in enumerate(jobs_data)]
    makespan = cp.intvar(0, horizon, name="makespan")

    model = cp.Model()

    # A task cannot start before the previous task of the same job has ended.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            model += start[j][t] >= start[j][t - 1] + job[t - 1][1]

    # A machine works on one task at a time: the tasks assigned to one machine never overlap.
    machines = sorted({machine for job in jobs_data for machine, _ in job})
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, (m, _) in enumerate(job) if m == machine]
        model += cp.NoOverlap([start[j][t] for j, t in tasks],
                              [jobs_data[j][t][1] for j, t in tasks])

    # The makespan is the latest end time; it is enough to look at the last task of each job.
    model += makespan == cp.max([start[j][-1] + job[-1][1] for j, job in enumerate(jobs_data)])
    model.minimize(makespan)

    return model, {"makespan": makespan}
