from pyscipopt import Model, quicksum

# Permutation flow shop: n jobs go through M machines in series, in the same order on
# every machine. Each machine works on one job at a time. Find the job sequence that
# minimises the makespan, the time when the last job leaves the last machine.
def build(instance):
    jobs = instance["jobs"]          # the jobs; process_time[i] is the row of jobs[i]
    machines = instance["machines"]  # the machines in processing order
    pt = instance["process_time"]    # pt[i][k] = time job i needs on machine k
    positions = instance["schedules"]  # the slots of the sequence, one job per slot
    n = len(jobs)
    M = len(machines)
    P = len(positions)
    # every job runs on every machine one after another: total work bounds the makespan
    horizon = sum(sum(row) for row in pt)

    m = Model()

    # x[i, p] = 1 if job i is the job in sequence slot p
    x = {(i, p): m.addVar(name=f"x_{i}_{p}", vtype="B") for i in range(n) for p in range(P)}
    # C[p, k] = time at which the job in slot p leaves machine k
    C = {(p, k): m.addVar(name=f"C_{p}_{k}", vtype="I", lb=0, ub=horizon)
         for p in range(P) for k in range(M)}
    makespan = m.addVar(name="makespan", vtype="I", lb=0, ub=horizon)

    # each job occupies exactly one slot
    for i in range(n):
        m.addCons(quicksum(x[i, p] for p in range(P)) == 1)
    # each slot holds exactly one job
    for p in range(P):
        m.addCons(quicksum(x[i, p] for i in range(n)) == 1)

    # processing time of the job in slot p on machine k
    def dur(p, k):
        return quicksum(pt[i][k] * x[i, p] for i in range(n))

    # a machine starts the job in slot p only after it has finished slot p-1
    # and the job has left machine k-1 (so it starts after the job's previous machine)
    for p in range(P):
        for k in range(M):
            # the job in slot p starts on machine k only when machine k is free again
            if p > 0:
                m.addCons(C[p, k] >= C[p - 1, k] + dur(p, k))
            # the job in slot p reaches machine k only after leaving machine k-1
            if k > 0:
                m.addCons(C[p, k] >= C[p, k - 1] + dur(p, k))
            # the first slot on the first machine starts at time zero
            if p == 0 and k == 0:
                m.addCons(C[p, k] >= dur(p, k))

    # the makespan is the completion time of the last slot on the last machine
    m.addCons(makespan == C[P - 1, M - 1])

    m.setObjective(makespan, "minimize")
    return m, {"makespan": makespan}
