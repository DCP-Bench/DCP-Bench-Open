# Flow shop scheduling: all jobs pass through the machines in the same order, one job
# at a time per machine; find the order of the jobs that minimizes the makespan, the time
# when the last job leaves the last machine.
import z3


def build(instance):
    process_time = instance["process_time"]  # process_time[job][machine]
    n_jobs = len(process_time)
    n_machines = len(process_time[0])
    # Upper bound on every time: all the work done one piece after the other.
    max_duration = sum(sum(row) for row in process_time)

    # The order of the jobs is a single sequence that every machine follows, so it is
    # described by before[i][j] (for i < j): true if job i comes before job j in the
    # sequence. This keeps the processing times constants in the timing constraints,
    # where a variable "job at place k" would need an If-sum to look its time up.
    before = {(i, j): z3.Bool(f"before_{i}_{j}")
              for i in range(n_jobs) for j in range(i + 1, n_jobs)}

    def comes_before(i, j):
        return before[(i, j)] if i < j else z3.Not(before[(j, i)])

    # Start time of every job on every machine, and the makespan.
    start = [[z3.Int(f"start_{j}_{m}") for m in range(n_machines)] for j in range(n_jobs)]
    makespan = z3.Int("makespan")

    solver = z3.Solver()

    # The order is a sequence: comes_before is transitive (no cycles).
    for i in range(n_jobs):
        for j in range(n_jobs):
            for k in range(n_jobs):
                if len({i, j, k}) == 3:
                    solver.add(z3.Implies(z3.And(comes_before(i, j), comes_before(j, k)),
                                          comes_before(i, k)))

    for j in range(n_jobs):
        for m in range(n_machines):
            # Times are between 0 and the total amount of work (the reference's bounds).
            solver.add(start[j][m] >= 0, start[j][m] + process_time[j][m] <= max_duration)
            # A job cannot start on machine m before it has finished on machine m - 1.
            if m > 0:
                solver.add(start[j][m] >= start[j][m - 1] + process_time[j][m - 1])

    # A machine handles one job at a time, in the order of the sequence: if job i comes
    # before job j, job j starts on every machine after job i has finished on it.
    for i in range(n_jobs):
        for j in range(i + 1, n_jobs):
            for m in range(n_machines):
                solver.add(z3.If(before[(i, j)],
                                 start[j][m] >= start[i][m] + process_time[i][m],
                                 start[i][m] >= start[j][m] + process_time[j][m]))

    # The makespan is the latest end time, which is that of some job on the last machine.
    last = n_machines - 1
    ends = [start[j][last] + process_time[j][last] for j in range(n_jobs)]
    for e in ends:
        solver.add(makespan >= e)
    solver.add(z3.Or([makespan == e for e in ends]))

    # Implied lower bound on the makespan: a machine m has to process all jobs, and cannot
    # start before the quickest job has passed the machines before it, and the last job
    # still has to pass the machines after it, at best the quickest tail.
    for m in range(n_machines):
        head = min(sum(process_time[j][:m]) for j in range(n_jobs))
        tail = min(sum(process_time[j][m + 1:]) for j in range(n_jobs))
        solver.add(makespan >= head + sum(process_time[j][m] for j in range(n_jobs)) + tail)

    # Minimize the makespan.
    return solver, {"makespan": makespan}, ("minimize", makespan)
