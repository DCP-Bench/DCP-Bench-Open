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

    # at[k][j] is true if the job in the k-th place of the sequence is job j. Booleans
    # with exactly-one constraints stand in for the sequence variable, because Z3 has no
    # element constraint to look up the processing time of "the job at place k".
    at = [[z3.Bool(f"at_{k}_{j}") for j in range(n_jobs)] for k in range(n_jobs)]
    # Start and end time of the k-th job of the sequence on each machine.
    start = [[z3.Int(f"start_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]
    end = [[z3.Int(f"end_{k}_{m}") for m in range(n_machines)] for k in range(n_jobs)]
    makespan = z3.Int("makespan")

    solver = z3.Solver()

    # Every job appears exactly once in the sequence.
    for k in range(n_jobs):
        solver.add(z3.PbEq([(at[k][j], 1) for j in range(n_jobs)], 1))
    for j in range(n_jobs):
        solver.add(z3.PbEq([(at[k][j], 1) for k in range(n_jobs)], 1))

    for k in range(n_jobs):
        for m in range(n_machines):
            solver.add(start[k][m] >= 0, start[k][m] <= max_duration)
            solver.add(end[k][m] >= 0, end[k][m] <= max_duration)
            # The k-th job of the sequence takes the processing time of its own job on machine m.
            time_km = z3.Sum([z3.If(at[k][j], process_time[j][m], 0) for j in range(n_jobs)])
            solver.add(end[k][m] == start[k][m] + time_km)
            # A job cannot start on machine m before it has finished on machine m - 1.
            if m > 0:
                solver.add(start[k][m] >= end[k][m - 1])
            # The k-th job cannot start on machine m before the (k - 1)-th has finished on it.
            if k > 0:
                solver.add(start[k][m] >= end[k - 1][m])

    # The makespan is the latest end time. End times only grow along the sequence and
    # along the machines, so that is the end of the last job on the last machine.
    solver.add(makespan == end[n_jobs - 1][n_machines - 1])
    solver.add(makespan >= 0, makespan <= max_duration)

    # Minimize the makespan.
    return solver, {"makespan": makespan}, ("minimize", makespan)
