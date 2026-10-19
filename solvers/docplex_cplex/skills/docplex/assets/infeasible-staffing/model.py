"""Infeasible: staff 3 shifts of 2 people each from 5 people, one shift per person.

Six places are needed and only five people exist, so the model has no solution.
The program reads the status instead of expecting an exception or a result.
"""
from docplex.mp.model import Model

PEOPLE = ["ann", "ben", "cem", "dia", "eli"]
SHIFTS = ["morning", "noon", "night"]
NEEDED = 2  # people per shift

m = Model(name="infeasible-staffing")
work = m.binary_var_matrix(PEOPLE, SHIFTS, name="work")  # keyed by (person, shift)

for s in SHIFTS:
    m.add_constraint(m.sum(work[p, s] for p in PEOPLE) == NEEDED)  # cover each shift
for p in PEOPLE:
    m.add_constraint(m.sum(work[p, s] for s in SHIFTS) <= 1)  # at most one shift each

m.minimize(m.sum(work.values()))  # the objective is not what matters here
sol = m.solve()

status = m.solve_details.status
if sol is None:
    print(f"No staffing plan exists: {status}")
else:
    print(f"Staffing plan found, objective {sol.objective_value:.0f}: {status}")
