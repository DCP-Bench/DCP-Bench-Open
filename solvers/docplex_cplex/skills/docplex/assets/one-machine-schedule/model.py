"""Scheduling: one machine, four tasks with release times and a precedence, minimise makespan.

No two tasks may overlap. Each pair gets an order binary and two indicator
constraints, one per order, so no big-M is needed.
"""
from docplex.mp.model import Model

NAMES = ["cut", "weld", "paint", "pack"]
DUR = [3, 2, 4, 2]
RELEASE = [0, 1, 0, 5]          # earliest start of each task
PRECEDES = [(0, 2)]             # task 0 must finish before task 2 starts
HORIZON = sum(DUR) + max(RELEASE)

m = Model(name="one-machine-schedule")
start = [m.integer_var(RELEASE[i], HORIZON, name=f"s_{NAMES[i]}") for i in range(len(DUR))]
makespan = m.integer_var(0, HORIZON, name="makespan")

for i in range(len(DUR)):
    m.add_constraint(makespan >= start[i] + DUR[i])

for i in range(len(DUR)):
    for j in range(i + 1, len(DUR)):
        before = m.binary_var(name=f"{NAMES[i]}_before_{NAMES[j]}")
        # before == 1: i runs first; before == 0: j runs first
        m.add_indicator(before, start[i] + DUR[i] <= start[j])
        m.add_indicator(before, start[j] + DUR[j] <= start[i], active_value=0)

for a, b in PRECEDES:
    m.add_constraint(start[a] + DUR[a] <= start[b])

m.minimize(makespan)
m.parameters.mip.tolerances.mipgap = 0  # the default 1e-4 may stop short of the optimum
sol = m.solve()
# Accept the result only on "integer optimal solution": anything else is not a proven answer.
if m.solve_details.status != "integer optimal solution":
    raise SystemExit(f"no proven-optimal schedule: {m.solve_details.status}")

print(f"Makespan: {sol.objective_value:.0f} ({m.solve_details.status})")
for i in sorted(range(len(DUR)), key=lambda k: sol[start[k]]):
    s = round(sol[start[i]])
    print(f"  {NAMES[i]:6s} starts {s:2d} ends {s + DUR[i]:2d}")
