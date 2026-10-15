# Permutation flow shop: find the job sequence that minimises the makespan.
# Jobs go through the machines 1..M in the same order, each machine works on one job
# at a time, and a job waits until the previous machine has finished it.
from paramita.modelling import Bool


def build(instance):
    jobs = instance["jobs"]
    machines = instance["machines"]
    ptime = instance["process_time"]  # ptime[j][m]: time of job index j on machine index m
    n, M = len(jobs), len(machines)

    # Upper bound on any completion time: all processing times in sequence.
    horizon = sum(sum(row) for row in ptime)
    width = max(1, horizon.bit_length())

    # x[j][p] = 1 if job j is at position p of the sequence (one-hot)
    x = [[Bool(f"x_{j}_{p}") for p in range(n)] for j in range(n)]

    cons = []
    # every job takes exactly one position in the sequence
    cons += [sum(x[j]) == 1 for j in range(n)]
    # every position holds exactly one job
    cons += [sum(x[j][p] for j in range(n)) == 1 for p in range(n)]

    # processing time of the job at position p on machine m
    def proc(p, m):
        return sum(ptime[j][m] * x[j][p] for j in range(n))

    # completion time of the job at position p on machine m, in binary
    def completion_var(p, m):
        bits = [Bool(f"c_{p}_{m}_{k}") for k in range(width)]
        return sum((1 << k) * bits[k] for k in range(width))

    C = [[completion_var(p, m) for m in range(M)] for p in range(n)]

    # a job starts on a machine only after the machine has finished the previous job
    # in the sequence, and the job's own processing on that machine takes its time
    for p in range(n):
        for m in range(M):
            if p > 0:
                cons.append(C[p][m] >= C[p - 1][m] + proc(p, m))
            if m > 0:
                cons.append(C[p][m] >= C[p][m - 1] + proc(p, m))
            if p == 0 and m == 0:
                cons.append(C[p][m] >= proc(p, m))

    # makespan: the time when the last job has been processed on the last machine
    makespan = C[n - 1][M - 1]
    return cons, {"makespan": makespan}, ("minimize", makespan)
