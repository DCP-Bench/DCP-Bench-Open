# Job shop scheduling: schedule the tasks of each job on their machines so that the makespan is minimal.
from pyscipopt import Model, quicksum


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] is the list of [machine, duration] tasks of job j, in order
    m = Model()

    # the horizon is the total duration of all tasks: a schedule that runs the tasks one after another fits in it
    horizon = sum(d for job in jobs for _, d in job)

    # start[j, t] is the start time of task t of job j
    start = {}
    for j, job in enumerate(jobs):
        for t, (_, d) in enumerate(job):
            start[j, t] = m.addVar(name=f"start[{j},{t}]", vtype="I", lb=0, ub=horizon - d)

    # the makespan is the time at which the last task finishes
    makespan = m.addVar(name="makespan", vtype="I", lb=0, ub=horizon)

    # no task for a job can be started until the previous task for that job is completed
    # (each task starts after its predecessor in the same job has finished)
    for j, job in enumerate(jobs):
        for t in range(len(job) - 1):
            d = job[t][1]
            m.addCons(start[j, t] + d <= start[j, t + 1])

    # the makespan is at least the completion time of the last task of every job
    for j, job in enumerate(jobs):
        t = len(job) - 1
        m.addCons(start[j, t] + job[t][1] <= makespan)

    # a machine can only work on one task at a time, and a task, once started, runs to completion:
    # for every pair of tasks on the same machine, one of the two must finish before the other starts
    tasks = [(j, t) for j, job in enumerate(jobs) for t in range(len(job))]
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            ja, ta = tasks[a]
            jb, tb = tasks[b]
            machine_a, da = jobs[ja][ta]
            machine_b, db = jobs[jb][tb]
            if machine_a != machine_b:
                continue
            # order[a, b] = 1 if task a runs before task b on the shared machine, 0 otherwise
            order = m.addVar(name=f"order[{ja},{ta},{jb},{tb}]", vtype="B")
            m.addConsIndicator(start[ja, ta] + da <= start[jb, tb], binvar=order)
            m.addConsIndicator(start[jb, tb] + db <= start[ja, ta], binvar=order, activeone=False)

    # the objective is the optimal makespan
    m.setObjective(makespan, "minimize")

    # outputs: the optimal makespan
    return m, {"makespan": makespan}
