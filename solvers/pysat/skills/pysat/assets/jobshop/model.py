"""Job shop (ft06): each job visits its machines in order; minimise the makespan."""
from pysat.examples.rc2 import RC2Stratified
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

# Fisher and Thompson ft06: each job is a list of (machine, duration).
JOBS = [
    [(2, 1), (0, 3), (1, 6), (3, 7), (5, 3), (4, 6)],
    [(1, 8), (2, 5), (4, 10), (5, 10), (0, 10), (3, 4)],
    [(2, 5), (3, 4), (5, 8), (0, 9), (1, 1), (4, 7)],
    [(1, 5), (0, 5), (2, 5), (3, 3), (4, 8), (5, 9)],
    [(2, 9), (1, 3), (4, 5), (5, 4), (0, 3), (3, 1)],
    [(1, 3), (3, 3), (5, 9), (0, 10), (4, 4), (2, 1)],
]


def greedy_makespan():
    """Upper bound: repeatedly start the operation that can begin earliest."""
    nxt = [0] * len(JOBS)
    job_free = [0] * len(JOBS)
    mach_free = {}
    end = 0
    for _ in range(sum(len(j) for j in JOBS)):
        best = None
        for j, job in enumerate(JOBS):
            if nxt[j] < len(job):
                m, d = job[nxt[j]]
                s = max(job_free[j], mach_free.get(m, 0))
                if best is None or s < best[0]:
                    best = (s, j, m, d)
        s, j, m, d = best
        job_free[j] = mach_free[m] = s + d
        nxt[j] += 1
        end = max(end, s + d)
    return end


def main():
    UB = greedy_makespan()                         # any feasible makespan is a valid horizon
    totals = [sum(d for _, d in job) for job in JOBS]
    loads = {}
    for job in JOBS:
        for m, d in job:
            loads[m] = loads.get(m, 0) + d
    LB = max(max(totals), max(loads.values()))     # trivial lower bound

    pool = IDPool()
    start = {}
    for j, job in enumerate(JOBS):                 # domains from head and tail sums
        head = 0
        for k, (_, d) in enumerate(job):
            tail = totals[j] - head - d
            start[j, k] = Integer(f"s{j}_{k}", head, UB - tail - d, encoding="order", vpool=pool)
            head += d
    makespan = Integer("makespan", LB, UB, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=list(start.values()) + [makespan], vpool=pool)

    for j, job in enumerate(JOBS):
        for k, (_, d) in enumerate(job):
            engine.add_linear(start[j, k] + d <= makespan)
            if k + 1 < len(job):
                engine.add_linear(start[j, k] + d <= start[j, k + 1])

    machines = {}
    for j, job in enumerate(JOBS):
        for k, (m, d) in enumerate(job):
            machines.setdefault(m, []).append((j, k, d))
    disjunctions = []                              # no overlap: one of the two orders holds
    for tasks in machines.values():
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                ja, ka, da = tasks[a]
                jb, kb, db = tasks[b]
                a_first = engine.add_linear(start[ja, ka] + da <= start[jb, kb], reified=True)
                b_first = engine.add_linear(start[jb, kb] + db <= start[ja, ka], reified=True)
                if a_first is not None and b_first is not None:   # None: already entailed, nothing to add
                    disjunctions.append([a_first, b_first])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)      # hard: precedences, bounds, reified orders
    for clause in disjunctions:
        formula.append(clause)
    for t in range(LB + 1, UB + 1):                # soft: unit cost for each threshold the makespan reaches
        formula.append([-makespan.ge(t)], weight=1)

    rc2 = RC2Stratified(formula, solver="glucose42")
    model = rc2.compute()
    rc2.delete()
    dense = [-v for v in range(1, pool.top + 1)]   # RC2 omits unused variables; decode needs all
    for lit in model:
        dense[abs(lit) - 1] = lit
    span = LB + rc2.cost
    times = [[start[j, k].decode(dense) for k in range(len(job))] for j, job in enumerate(JOBS)]
    print("Makespan:", span)
    print("Greedy bound:", UB, "lower bound:", LB)
    print("Schedule valid:", is_valid(times, span))
    for j, row in enumerate(times):
        print(f"Job {j}:", row)


def is_valid(times, span):
    """Independent check: job order, no two operations overlapping on a machine, makespan."""
    for j, job in enumerate(JOBS):
        for k, (_, d) in enumerate(job):
            if times[j][k] + d > span or times[j][k] < 0:
                return False
            if k + 1 < len(job) and times[j][k] + d > times[j][k + 1]:
                return False
    ops = [(m, times[j][k], times[j][k] + d) for j, job in enumerate(JOBS) for k, (m, d) in enumerate(job)]
    return all(e1 <= s2 or e2 <= s1 for i, (m1, s1, e1) in enumerate(ops)
               for m2, s2, e2 in ops[i + 1:] if m1 == m2)


if __name__ == "__main__":
    main()
