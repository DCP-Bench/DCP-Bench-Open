from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

# One machine, three jobs with durations and deadlines; no two jobs overlap.
# Each start time is one-hot. run[j][t] says job j is running during slot t.
durations = [2, 3, 2]
deadlines = [4, 7, 5]          # job j must finish by deadlines[j]
horizon = max(deadlines)
jobs = len(durations)

start = []
for j, d in enumerate(durations):
    latest = deadlines[j] - d  # latest start that still meets the deadline
    start.append({t: Bool(f"s_{j}_{t}") for t in range(latest + 1)})

run = [[Bool(f"run_{j}_{t}") for t in range(horizon)] for j in range(jobs)]
constraints = []
for j in range(jobs):
    constraints.append(sum(start[j].values()) == 1)            # exactly one start
    for t in range(horizon):
        # job j runs in slot t iff it started in slot t - durations[j] + 1 .. t
        begins = [start[j][u] for u in start[j] if u <= t < u + durations[j]]
        if begins:
            constraints.append(run[j][t] == (sum(begins) >= 1))
        else:
            constraints.append(~run[j][t])
for t in range(horizon):
    constraints.append(sum(run[j][t] for j in range(jobs)) <= 1)  # the machine does one job at a time

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)

if not solver.solve():
    print("unsatisfiable")
else:
    true = {abs(lit) for lit in solver.model() if lit > 0}
    for j in range(jobs):
        t0 = next(t for t, b in start[j].items() if pool.get_variable(b) in true)
        print(f"job {j} starts at {t0} and ends at {t0 + durations[j]} (deadline {deadlines[j]})")
