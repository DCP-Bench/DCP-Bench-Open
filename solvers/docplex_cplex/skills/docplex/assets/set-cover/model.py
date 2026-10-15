"""Minimise: fewest sets whose union covers every element."""
from docplex.mp.model import Model

ELEMENTS = range(1, 7)
SETS = {
    "A": {1, 2, 3},
    "B": {2, 4},
    "C": {3, 5},
    "D": {4, 5, 6},
    "E": {1, 6},
}

m = Model(name="set-cover")
pick = m.binary_var_dict(SETS.keys(), name="pick")  # keyed by set name

for e in ELEMENTS:
    # element e is covered by at least one chosen set that contains it
    m.add_constraint(m.sum(pick[s] for s in SETS if e in SETS[s]) >= 1)

m.minimize(m.sum(pick.values()))
m.parameters.mip.tolerances.mipgap = 0  # the default 1e-4 may stop short of the optimum
sol = m.solve()
# Accept the result only on "integer optimal solution": anything else is not a proven answer.
if m.solve_details.status != "integer optimal solution":
    raise SystemExit(f"no proven-optimal cover: {m.solve_details.status}")

chosen = [s for s in SETS if sol[pick[s]] > 0.5]
print(f"Sets chosen: {len(chosen)} ({m.solve_details.status})")
print("  " + ", ".join(chosen))
