# Flowshop scheduling: a set of jobs must be processed on a set of machines in series. All jobs have the same
# processing order through the machines, from machine 1 to machine M. The time to process job j on machine m is
# process_time[j][m]. Find the sequence of jobs that minimises the makespan, the time when all jobs have been processed.
import mip


def build(instance):
    n = len(instance["jobs"])
    num_machines = len(instance["machines"])
    pt = instance["process_time"]
    total = sum(pt[j][m] for j in range(n) for m in range(num_machines))

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[j][p] = 1 when job j is at position p of the sequence.
    x = [[model.add_var(f"x_{j}_{p}", var_type=mip.BINARY) for p in range(n)] for j in range(n)]

    # Each job takes exactly one position in the sequence.
    for j in range(n):
        model += mip.xsum(x[j][p] for p in range(n)) == 1

    # Each position is taken by exactly one job.
    for p in range(n):
        model += mip.xsum(x[j][p] for j in range(n)) == 1

    # The first job of the sequence goes to the first machine; the other jobs wait. Then the completion time of
    # position p on machine m is after the completion of position p on machine m-1 (the job moves on in series)
    # and after the completion of position p-1 on machine m (the machine works on one job at a time).
    c = [
        [model.add_var(f"c_{p}_{m}", lb=0, ub=total, var_type=mip.INTEGER) for m in range(num_machines)]
        for p in range(n)
    ]
    for p in range(n):
        for m in range(num_machines):
            # Processing time of the job at position p on machine m.
            proc = mip.xsum(pt[j][m] * x[j][p] for j in range(n))
            if p == 0 and m == 0:
                model += c[0][0] >= proc
            if p > 0:
                model += c[p][m] >= c[p - 1][m] + proc
            if m > 0:
                model += c[p][m] >= c[p][m - 1] + proc

    # The makespan is the time when the last job has been processed on the last machine.
    makespan = model.add_var("makespan", lb=0, ub=total, var_type=mip.INTEGER)
    model += makespan == c[n - 1][num_machines - 1]

    model.objective = makespan
    return model, {"makespan": makespan}
