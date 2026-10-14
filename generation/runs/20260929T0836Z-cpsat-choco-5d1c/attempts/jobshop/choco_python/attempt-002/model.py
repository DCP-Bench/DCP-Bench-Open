# Job shop: every job is a chain of tasks, each on a given machine for a given
# time, run in order. A machine works on one task at a time and a task runs
# without interruption. Minimise the time at which the last task finishes.
from pychoco.model import Model


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = list of (machine, duration) tasks in order
    horizon = sum(duration for job in jobs for _, duration in job)  # running tasks one by one always fits

    model = Model()

    tasks_on_machine = {}  # machine -> the task objects of all tasks that use it
    ends = []
    for j, job in enumerate(jobs):
        previous_end = None
        for k, (machine, duration) in enumerate(job):
            start = model.intvar(0, horizon, name=f"start_{j}_{k}")
            end = model.intvar(0, horizon, name=f"end_{j}_{k}")
            # the task runs for its duration without interruption
            task = model.task(start, duration, end)
            task.ensure_bound_consistency()
            tasks_on_machine.setdefault(machine, []).append(task)
            # a task cannot start before the previous task of its job has ended
            if previous_end is not None:
                model.arithm(start, ">=", previous_end).post()
            previous_end = end
            ends.append(end)

    # A machine works on one task at a time: it is a resource of capacity 1 that
    # every task on it uses with height 1. Choco's cumulative constraint filters
    # much more than pairwise "one starts after the other" disjunctions.
    one = model.intvar(1, 1, name="one")
    for machine_tasks in tasks_on_machine.values():
        model.cumulative(machine_tasks, [one] * len(machine_tasks), one).post()

    # the makespan is when the last task ends, to be minimised
    makespan = model.intvar(0, horizon, name="makespan")
    model.max(makespan, ends).post()

    return model, {"makespan": makespan}, ("minimize", makespan)
