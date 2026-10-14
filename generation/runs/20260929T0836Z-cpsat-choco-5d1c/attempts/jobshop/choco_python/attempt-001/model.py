# Job shop: every job is a chain of tasks, each on a given machine for a given
# time, run in order. A machine works on one task at a time and a task runs
# without interruption. Minimise the time at which the last task finishes.
from itertools import combinations

from pychoco.model import Model


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = list of (machine, duration) tasks in order
    horizon = sum(duration for job in jobs for _, duration in job)  # running tasks one by one always fits

    model = Model()

    tasks_on_machine = {}  # machine -> the (start, end) variables of all tasks that use it
    ends = []
    for j, job in enumerate(jobs):
        previous_end = None
        for k, (machine, duration) in enumerate(job):
            start = model.intvar(0, horizon, name=f"start_{j}_{k}")
            end = model.intvar(0, horizon, name=f"end_{j}_{k}")
            # the task runs for its duration without interruption
            model.arithm(end, "-", start, "=", duration).post()
            tasks_on_machine.setdefault(machine, []).append((start, end))
            # a task cannot start before the previous task of its job has ended
            if previous_end is not None:
                model.arithm(start, ">=", previous_end).post()
            previous_end = end
            ends.append(end)

    # a machine works on one task at a time: of any two tasks on the same
    # machine, one starts only after the other has ended
    for machine_tasks in tasks_on_machine.values():
        for (start1, end1), (start2, end2) in combinations(machine_tasks, 2):
            model.or_([model.arithm(start1, ">=", end2), model.arithm(start2, ">=", end1)]).post()

    # the makespan is when the last task ends, to be minimised
    makespan = model.intvar(0, horizon, name="makespan")
    model.max(makespan, ends).post()

    return model, {"makespan": makespan}, ("minimize", makespan)
