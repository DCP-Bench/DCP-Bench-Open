# Job shop: jobs are ordered sequences of tasks on machines; schedule them so that
# no machine runs two tasks at once and the makespan (last completion time) is minimal.
from paramita.modelling import Bool, If


def _int(name, ub):
    # Integer in [0, ub] as binary bits: value = sum of 2**k * bit_k.
    # Binary because the range (sum of durations) is wide and times are compared pairwise.
    nb = max(1, ub.bit_length())
    bits = [Bool(f"{name}_b{k}") for k in range(nb)]
    value = sum((2 ** k) * b for k, b in enumerate(bits))
    return value, [value <= ub]


def build(instance):
    jobs = instance["jobs_data"]  # jobs[j] = [[machine, duration], ...] in processing order

    # Horizon: the sum of all durations bounds the makespan of any schedule.
    horizon = sum(d for job in jobs for _, d in job)

    cons = []
    start = {}
    for j, job in enumerate(jobs):
        for k in range(len(job)):
            s, c = _int(f"start_{j}_{k}", horizon)
            start[j, k] = s
            cons += c

    # No task for a job can be started until the previous task for that job is completed.
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            cons.append(start[j, k] + job[k][1] <= start[j, k + 1])

    # A machine can only work on one task at a time: for each pair of tasks on the same
    # machine, one of them completes before the other starts. A task, once started, runs to
    # completion, so its end is start + duration.
    by_machine = {}
    for j, job in enumerate(jobs):
        for k, (machine, _) in enumerate(job):
            by_machine.setdefault(machine, []).append((j, k))
    for machine, tasks in sorted(by_machine.items()):
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                j1, k1 = tasks[a]
                j2, k2 = tasks[b]
                d1 = jobs[j1][k1][1]
                d2 = jobs[j2][k2][1]
                first = Bool(f"first_m{machine}_{j1}_{k1}_{j2}_{k2}")
                cons.append(If(first, start[j1, k1] + d1 <= start[j2, k2]))
                cons.append(If(~first, start[j2, k2] + d2 <= start[j1, k1]))

    # The makespan is the total time taken to complete all jobs: every job's last task
    # completes no later than the makespan.
    makespan, c = _int("makespan", horizon)
    cons += c
    for j, job in enumerate(jobs):
        if job:
            k = len(job) - 1
            cons.append(start[j, k] + job[k][1] <= makespan)

    return cons, {"makespan": makespan}, ("minimize", makespan)
