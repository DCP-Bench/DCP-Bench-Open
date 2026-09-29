# Job shop: every job is a chain of tasks, each on a given machine for a given
# time, run in order. A machine works on one task at a time and a task runs
# without interruption. Minimise the time at which the last task finishes.
from ortools.sat.python import cp_model


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = list of (machine, duration) tasks in order
    horizon = sum(duration for job in jobs for _, duration in job)  # running tasks one by one always fits

    model = cp_model.CpModel()

    intervals_on_machine = {}  # machine -> the intervals of all tasks that use it
    ends = []
    for j, job in enumerate(jobs):
        previous_end = None
        for k, (machine, duration) in enumerate(job):
            start = model.new_int_var(0, horizon, f"start_{j}_{k}")
            end = model.new_int_var(0, horizon, f"end_{j}_{k}")
            # the task runs for its duration without interruption
            interval = model.new_interval_var(start, duration, end, f"task_{j}_{k}")
            intervals_on_machine.setdefault(machine, []).append(interval)
            # a task cannot start before the previous task of its job has ended
            if previous_end is not None:
                model.add(start >= previous_end)
            previous_end = end
            ends.append(end)

    # a machine works on one task at a time
    for machine_intervals in intervals_on_machine.values():
        model.add_no_overlap(machine_intervals)

    # the makespan is when the last task ends, to be minimised
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, ends)
    model.minimize(makespan)

    return model, {"makespan": makespan}
