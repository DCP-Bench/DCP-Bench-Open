# Job shop: every job is a chain of tasks, each on a given machine for a given
# time, run in order. A machine works on one task at a time and a task runs
# without interruption. Minimise the time at which the last task finishes.
from itertools import combinations

from pychoco.model import Model


def greedy_schedule(jobs):
    """Start times of one feasible schedule, keyed by (job, position).

    Repeatedly start, among the next unscheduled task of every job, the one that
    can start earliest (its job's previous task done and its machine free). This
    is a valid schedule, so the optimum is never longer than it.
    """
    next_task = [0] * len(jobs)
    job_ready = [0] * len(jobs)
    machine_ready = {}
    starts = {}
    while True:
        best = None
        for j, job in enumerate(jobs):
            if next_task[j] < len(job):
                machine, _ = job[next_task[j]]
                start = max(job_ready[j], machine_ready.get(machine, 0))
                if best is None or start < best[0]:
                    best = (start, j)
        if best is None:
            return starts
        start, j = best
        machine, duration = jobs[j][next_task[j]]
        starts[j, next_task[j]] = start
        job_ready[j] = machine_ready[machine] = start + duration
        next_task[j] += 1


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = list of (machine, duration) tasks in order

    # Bounds on the makespan from the instance: no machine finishes before it has
    # done all its work and no job before all its tasks have run (lower bound);
    # the greedy schedule above is feasible (upper bound, the horizon).
    machine_load = {}
    for job in jobs:
        for machine, duration in job:
            machine_load[machine] = machine_load.get(machine, 0) + duration
    lower = max(list(machine_load.values()) + [sum(d for _, d in job) for job in jobs])
    greedy = greedy_schedule(jobs)
    horizon = max((greedy[j, k] + d for j, job in enumerate(jobs)
                   for k, (_, d) in enumerate(job)), default=0)

    model = Model()

    tasks = {}  # (job, position) -> (start variable, duration, machine)
    on_machine = {}  # machine -> the (job, position) keys of the tasks that use it
    for j, job in enumerate(jobs):
        before = 0  # work of this job that has to be done before this task
        after = sum(d for _, d in job)  # work of this job from this task on
        for k, (machine, duration) in enumerate(job):
            # a task starts after the earlier tasks of its job and leaves room for the later ones
            start = model.intvar(before, horizon - after, name=f"start_{j}_{k}")
            tasks[j, k] = (start, duration, machine)
            on_machine.setdefault(machine, []).append((j, k))
            before += duration
            after -= duration

    for j, job in enumerate(jobs):
        for k in range(1, len(job)):
            start, _, _ = tasks[j, k]
            previous, previous_duration, _ = tasks[j, k - 1]
            # a task cannot start before the previous task of its job has ended
            model.arithm(start, "-", previous, ">=", previous_duration).post()

    # A machine works on one task at a time: of any two tasks on the same machine,
    # exactly one runs first and the other starts after it has ended. The two
    # Booleans per pair give the search the order decisions that suit job shop.
    # Only the declaration order is a choice here, not the constraints: machines
    # come busiest first, and in each pair the Boolean "the task the greedy
    # schedule ran later goes first" is declared before its opposite, so that
    # Choco's default search, which breaks ties by declaration order and tries
    # the smallest value first, is steered towards the greedy order on the
    # busiest machine.
    for machine in sorted(on_machine, key=lambda m: -machine_load[m]):
        keys = sorted(on_machine[machine], key=lambda key: greedy[key])
        for x, y in combinations(keys, 2):
            start_x, duration_x, _ = tasks[x]
            start_y, duration_y, _ = tasks[y]
            y_first = model.arithm(start_x, "-", start_y, ">=", duration_y).reify()
            x_first = model.arithm(start_y, "-", start_x, ">=", duration_x).reify()
            model.arithm(x_first, "+", y_first, "=", 1).post()

    # The same rule again as a capacity-1 resource, whose propagation reasons over
    # all tasks of a machine at once rather than pair by pair.
    one = model.intvar(1, 1, name="one")
    for keys in on_machine.values():
        machine_tasks = [model.task(tasks[key][0], tasks[key][1]) for key in keys]
        model.cumulative(machine_tasks, [one] * len(machine_tasks), one).post()

    # Each task starts as early as its job and its machine order allow: at time 0,
    # when the previous task of its job ends, or when another task on its machine
    # ends. Moving every task left this way never lengthens a schedule, so the
    # optimal makespan is unchanged; it removes the schedules that differ only by
    # idle time slipped in before a task, which the runner would otherwise have to
    # enumerate one by one while proving that no other makespan is optimal.
    for (j, k), (start, _, machine) in tasks.items():
        options = []
        if k == 0:
            options.append(model.arithm(start, "=", 0))
        else:
            previous, previous_duration, _ = tasks[j, k - 1]
            options.append(model.arithm(start, "-", previous, "=", previous_duration))
        for other in on_machine[machine]:
            if other != (j, k):
                other_start, other_duration, _ = tasks[other]
                options.append(model.arithm(start, "-", other_start, "=", other_duration))
        model.or_(options).post()

    # the makespan is when the last task of any job ends, to be minimised
    makespan = model.intvar(lower, horizon, name="makespan")
    last_ends = []
    for j, job in enumerate(jobs):
        start, duration, _ = tasks[j, len(job) - 1]
        end = model.intvar(0, horizon, name=f"end_{j}")
        model.arithm(end, "-", start, "=", duration).post()
        last_ends.append(end)
    model.max(makespan, last_ends).post()

    return model, {"makespan": makespan}, ("minimize", makespan)
