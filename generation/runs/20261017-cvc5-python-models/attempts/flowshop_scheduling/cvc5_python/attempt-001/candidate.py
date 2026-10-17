# Flowshop scheduling: jobs must be processed on machines 1..M in series, with
# the same processing order through all machines. Minimise the makespan, the
# time when all jobs have been processed.
import cvc5.pythonic as cz


def build(instance):
    pt = instance["process_time"]
    n = len(instance["jobs"])
    m = len(instance["machines"])
    horizon = sum(sum(row) for row in pt)

    # A sequence of jobs: seq[p] is the job at position p of the order.
    seq = [cz.Int(f"seq_{p}") for p in range(n)]
    # Processing time of the job at position p on machine k.
    dur = [[cz.Int(f"dur_{p}_{k}") for k in range(m)] for p in range(n)]
    # Start time of the job at position p on machine k.
    start = [[cz.Int(f"start_{p}_{k}") for k in range(m)] for p in range(n)]
    makespan = cz.Int("makespan")

    cons = []

    # The sequence is a permutation of the jobs, indexed 0-based.
    # Bounds and no duplicates.
    cons.append(cz.Distinct(seq) if n >= 2 else seq[0] == 0)
    for p in range(n):
        cons.append(seq[p] >= 0)
        cons.append(seq[p] <= n - 1)

    # Each job's processing time on each machine comes from the data for
    # the job in that position.
    # Processing time of the job at each position on each machine.
    for p in range(n):
        for k in range(m):
            if n == 1:
                cons.append(dur[p][k] == pt[0][k])
            else:
                cons.append(
                    cz.Or([cz.And(seq[p] == j, dur[p][k] == pt[j][k]) for j in range(n)])
                )

    # Each job starts only after it has finished on the previous machine, and
    # each machine starts a job only after it has finished the previous job.
    # Start times are the latest of these two ends, and nothing starts before
    # time 0.
    # Time for a job to start on a machine.
    for p in range(n):
        for k in range(m):
            cons.append(start[p][k] >= 0)
            cons.append(start[p][k] <= horizon)
            candidates = []
            if p > 0:
                candidates.append(start[p - 1][k] + dur[p - 1][k])
            if k > 0:
                candidates.append(start[p][k - 1] + dur[p][k - 1])
            if not candidates:
                cons.append(start[p][k] == 0)
            elif len(candidates) == 1:
                cons.append(start[p][k] == candidates[0])
            else:
                cons.append(cz.And([start[p][k] >= c for c in candidates]))
                cons.append(cz.Or([start[p][k] == c for c in candidates]))

    # The makespan is the completion time of the last job on the last machine,
    # which is the latest completion time in the schedule.
    cons.append(makespan == start[n - 1][m - 1] + dur[n - 1][m - 1])

    return cons, {"makespan": makespan}, ("minimize", makespan)
