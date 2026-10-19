"""Feasibility check and objective for job-shop. A solution is {"start": [[start per task] per job]}."""


def feasible(instance, solution):
    jobs = instance["jobs"]
    s = solution.get("start")
    if (not isinstance(s, list) or len(s) != len(jobs)
            or any(not isinstance(row, list) or len(row) != len(job) for row, job in zip(s, jobs))):
        return ["'start' must have one list per job, one start time per task"]
    if any(type(t) is not int or t < 0 for row in s for t in row):
        return ["every start time must be a non-negative integer"]
    errors = []
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            if s[j][k] + job[k][1] > s[j][k + 1]:
                errors.append(f"job {j}: task {k + 1} starts before task {k} ends")
    tasks = [(m, s[j][k], s[j][k] + dur, j, k) for j, job in enumerate(jobs) for k, (m, dur) in enumerate(job)]
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            ma, sa, ea, ja, ka = tasks[a]
            mb, sb, eb, jb, kb = tasks[b]
            if ma == mb and sa < eb and sb < ea:
                errors.append(f"machine {ma}: job {ja} task {ka} overlaps job {jb} task {kb}")
    return errors


def objective(instance, solution):
    return max(s[-1] + job[-1][1] for s, job in zip(solution["start"], instance["jobs"]))
