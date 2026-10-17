# Job shop scheduling: several jobs, each a sequence of tasks that must run on
# specific machines in a given order. Minimise the makespan, the time it takes
# for all the jobs to be completed.
import mip


def build(instance):
    jobs_data = instance["jobs_data"]

    # Horizon: the sum of all task durations. Every start in a left-justified
    # schedule is at most this sum minus the task's own duration, so it is a
    # valid big-M computed from the data.
    horizon = 0
    for job in jobs_data:
        for machine, duration in job:
            horizon += duration

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # start[j][t]: start time of task t of job j
    start = []
    for j, job in enumerate(jobs_data):
        row = []
        for t, (machine, duration) in enumerate(job):
            row.append(
                model.add_var(
                    name=f"s_{j}_{t}",
                    lb=0,
                    ub=horizon - duration,
                    var_type=mip.INTEGER,
                )
            )
        start.append(row)

    makespan = model.add_var(name="makespan", lb=0, ub=horizon, var_type=mip.INTEGER)

    # No task for a job can be started until the previous task for that job is completed.
    for j, job in enumerate(jobs_data):
        for t in range(len(job) - 1):
            model.add_constr(start[j][t + 1] >= start[j][t] + job[t][1])

    # The time it takes for all the jobs to be completed (the makespan) is at least
    # the completion time of the last task of every job; a task, once started,
    # runs to completion for its full duration.
    for j, job in enumerate(jobs_data):
        if len(job) == 0:
            continue
        last = len(job) - 1
        model.add_constr(makespan >= start[j][last] + job[last][1])

    # A machine can only work on one task at a time.
    tasks_on = {}
    for j, job in enumerate(jobs_data):
        for t, (machine, duration) in enumerate(job):
            tasks_on.setdefault(machine, []).append((j, t, duration))

    for machine in sorted(tasks_on):
        tasks = tasks_on[machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                ja, ta, da = tasks[a]
                jb, tb, db = tasks[b]
                if ja == jb:
                    # tasks of one job are already ordered by the precedences
                    continue
                # before = 1: task a of job ja runs before task b of job jb
                before = model.add_var(
                    name=f"before_{ja}_{ta}_{jb}_{tb}", var_type=mip.BINARY
                )
                model.add_constr(
                    start[jb][tb] >= start[ja][ta] + da - horizon * (1 - before)
                )
                model.add_constr(
                    start[ja][ta] >= start[jb][tb] + db - horizon * before
                )

    model.objective = makespan
    return model, {"makespan": makespan}
