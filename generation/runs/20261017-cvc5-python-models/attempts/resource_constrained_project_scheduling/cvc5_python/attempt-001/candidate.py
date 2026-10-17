# Resource-constrained project scheduling: start times for the jobs that respect
# the precedence links, keep every renewable resource within its capacity at all
# times, and minimise the makespan.
import cvc5.pythonic as cz


def build(instance):
    dur = instance["durations_data"]
    need = instance["resource_needs_data"]
    cap = instance["resource_capacities_data"]
    succ = instance["successors_link_data"]
    n = len(dur)
    R = len(cap)
    # A serial schedule (one job after another) fits every resource, so the
    # optimal makespan, and every job's end, is at most the sum of durations.
    horizon = sum(dur)

    start = [cz.Int(f"start_{j}") for j in range(n)]
    makespan = cz.Int("makespan")

    constraints = []

    # Start times are non-negative integers, and the list starts from time 0.
    # Job 0 has no predecessor and is the first job of the instance data, so it starts at 0.
    for j in range(n):
        constraints.append(start[j] >= 0)
    constraints.append(start[0] == 0)

    # the makespan is the end time of the last job; every job ends by the makespan
    constraints.append(makespan >= 0)
    constraints.append(makespan <= horizon)
    for j in range(n):
        constraints.append(start[j] + dur[j] <= makespan)

    # precedence: a successor starts only after its predecessor has finished
    for a, b in succ:
        constraints.append(start[b] >= start[a] + dur[a])

    # resource capacity: at every time point, the jobs running at that time
    # use no more than the capacity of each resource
    for r in range(R):
        users = [j for j in range(n) if need[j][r] > 0 and dur[j] > 0]
        if not users:
            continue
        for t in range(horizon):
            usage = [
                cz.If(cz.And(start[j] <= t, t < start[j] + dur[j]), need[j][r], 0)
                for j in users
            ]
            constraints.append(cz.Sum(usage) <= cap[r])

    outputs = {"start_time": start}
    return constraints, outputs, ("minimize", makespan)
