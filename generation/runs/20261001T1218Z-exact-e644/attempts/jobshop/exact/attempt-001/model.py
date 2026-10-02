# Job shop: every job is a sequence of tasks, each needing one machine for a fixed duration. A task
# cannot start before the previous task of its job has finished, a machine runs one task at a
# time, and a task runs to completion once started. Minimise the makespan, the time at which the
# last task finishes.
from exact import Exact


def build(instance):
    jobs_data = instance["jobs_data"]  # jobs_data[j][t] = [machine, duration] of task t of job j
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    machine = {(j, t): jobs_data[j][t][0] for j, t in tasks}
    duration = {(j, t): jobs_data[j][t][1] for j, t in tasks}

    # Time horizon: the length of a schedule built greedily (always schedule the job whose next
    # task can begin earliest). Some schedule is at least this good, so the optimal makespan and
    # every start time of an optimal schedule are below it; it is also the "big M" of the
    # either-or constraints below. (The reference uses the sum of all durations, which is larger.)
    job_ready = [0] * len(jobs_data)
    machine_free = {}
    next_task = [0] * len(jobs_data)
    for _ in tasks:
        candidates = [(max(job_ready[j], machine_free.get(machine[j, next_task[j]], 0)), j)
                      for j in range(len(jobs_data)) if next_task[j] < len(jobs_data[j])]
        begin, j = min(candidates)
        t = next_task[j]
        job_ready[j] = machine_free[machine[j, t]] = begin + duration[j, t]
        next_task[j] += 1
    horizon = max(job_ready)

    # Lower bound on the makespan: a job needs the sum of its durations, and a machine needs its
    # total load plus the least time before its first task can begin (the work earlier in that
    # task's job) and after its last task (the work later in that task's job).
    head = {(j, t): sum(duration[j, s] for s in range(t)) for j, t in tasks}
    tail = {(j, t): sum(duration[j, s] for s in range(t + 1, len(jobs_data[j]))) for j, t in tasks}
    on_machine = {}
    for task in tasks:
        on_machine.setdefault(machine[task], []).append(task)
    head_min = {m: min(head[task] for task in ts) for m, ts in on_machine.items()}
    tail_min = {m: min(tail[task] for task in ts) for m, ts in on_machine.items()}
    lower = max([sum(d for _, d in job) for job in jobs_data]
                + [head_min[m] + sum(duration[task] for task in ts) + tail_min[m]
                   for m, ts in on_machine.items()])

    solver = Exact()

    # start[j,t] is the start time of task t of job j
    start = {task: f"start_{task[0]}_{task[1]}" for task in tasks}
    for task in tasks:
        solver.addVariable(start[task], 0, horizon)

    # no task can start before the previous task of its job has ended
    for j, t in tasks:
        if t > 0:
            solver.addConstraint([(1, start[j, t]), (-1, start[j, t - 1])], True, duration[j, t - 1])

    # A machine can work on one task at a time: for two tasks a, b on a machine either a is before
    # b (b starts after a ends) or b is before a. before[a, b] = 1 means a is before b, and the
    # horizon is the big M that switches the other alternative off.
    before = {}
    for m, ts in on_machine.items():
        for x in range(len(ts)):
            for y in range(x + 1, len(ts)):
                a, b = ts[x], ts[y]
                before[a, b] = f"task_{a[0]}_{a[1]}_before_{b[0]}_{b[1]}"
                solver.addVariable(before[a, b], 0, 1)
                # before[a,b] = 1  ->  start[b] >= start[a] + duration[a]
                solver.addConstraint([(1, start[b]), (-1, start[a]), (-horizon, before[a, b])],
                                     True, duration[a] - horizon)
                # before[a,b] = 0  ->  start[a] >= start[b] + duration[b]
                solver.addConstraint([(1, start[a]), (-1, start[b]), (horizon, before[a, b])],
                                     True, duration[b])
        # the order on a machine is a total order: no cyclic triple (implied, but it spares the
        # solver from discovering cycles through the start times)
        for x in range(len(ts)):
            for y in range(x + 1, len(ts)):
                for z in range(y + 1, len(ts)):
                    solver.addConstraint([(1, before[ts[x], ts[y]]), (1, before[ts[y], ts[z]]),
                                          (-1, before[ts[x], ts[z]])], True, 0, True, 1)

    def precedes(a, b):
        """Linear form (terms, constant) of 'task a is before task b on their machine'."""
        if (a, b) in before:
            return [(1, before[a, b])], 0
        return [(-1, before[b, a])], 1

    # makespan: the time at which the last task finishes
    solver.addVariable("makespan", min(lower, horizon), horizon)
    for j, job in enumerate(jobs_data):
        if not job:
            continue
        last = (j, len(job) - 1)
        solver.addConstraint([(1, "makespan"), (-1, start[last])], True, duration[last])

    # Implied constraints that state the load of a machine in a form the solver can bound with.
    for m, ts in on_machine.items():
        for a in ts:
            # everything before a on its machine has to be done before a starts there:
            # start[a] >= head_min[m] + sum of durations of the tasks before a
            terms, rhs = [(1, start[a])], head_min[m]
            for b in ts:
                if b != a and duration[b]:
                    t, c = precedes(b, a)
                    terms += [(-duration[b] * coef, name) for coef, name in t]
                    rhs += duration[b] * c
            solver.addConstraint(terms, True, rhs)
            # a and the tasks after it on its machine still have to run, and the last of them has
            # tail_min[m] left in its job: makespan >= start[a] + duration[a] + (durations after a)
            # + tail_min[m]
            terms, rhs = [(1, "makespan"), (-1, start[a])], duration[a] + tail_min[m]
            for b in ts:
                if b != a and duration[b]:
                    t, c = precedes(a, b)
                    terms += [(-duration[b] * coef, name) for coef, name in t]
                    rhs += duration[b] * c
            solver.addConstraint(terms, True, rhs)

    return solver, {"makespan": "makespan"}, ("minimize", [(1, "makespan")])
