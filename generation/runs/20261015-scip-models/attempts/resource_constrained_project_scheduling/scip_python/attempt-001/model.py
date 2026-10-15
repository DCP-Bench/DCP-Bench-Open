# Resource-constrained project scheduling: start each job so that the makespan is minimal,
# every precedence is respected and no resource capacity is exceeded at any time.
from pyscipopt import Model


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]
    capacities = instance["resource_capacities_data"]
    links = instance["successors_link_data"]

    n = len(durations)
    n_res = len(capacities)
    # no job starts after all durations are added up, so this bounds every start time
    horizon = sum(durations)

    m = Model()
    start = [m.addVar(name=f"start_{j}", vtype="I", lb=0, ub=horizon) for j in range(n)]
    makespan = m.addVar(name="makespan", vtype="I", lb=0, ub=horizon)

    # a job finishes at its start time plus its duration, and the project ends when the last job finishes
    for j in range(n):
        m.addCons(start[j] + durations[j] <= makespan)

    # each successor link [i, j] means job j starts only after job i has finished
    for i, j in links:
        m.addCons(start[i] + durations[i] <= start[j])

    # for each renewable resource, the jobs running at any time use at most its capacity
    for r in range(n_res):
        m.addConsCumulative(
            start,
            durations,
            [needs[j][r] for j in range(n)],
            capacities[r],
        )

    # minimise the project duration (makespan)
    m.setObjective(makespan, "minimize")

    # the output gives the start time of each job, numbered from 0
    return m, {"start_time": start}
