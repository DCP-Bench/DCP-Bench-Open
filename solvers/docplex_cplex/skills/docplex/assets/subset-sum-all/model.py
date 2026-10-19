"""All solutions: every subset of the numbers that sums to a target.

Each found solution is excluded with a no-good cut over the decision binaries, and
the model is solved again. For more than a few dozen solutions, the solution pool
(`populate()`) is much faster.
"""
from docplex.mp.model import Model

NUMBERS = [3, 5, 6, 7, 9, 11]
TARGET = 14

m = Model(name="subset-sum-all")
take = m.binary_var_list(len(NUMBERS), name="take")
m.add_constraint(m.scal_prod(take, NUMBERS) == TARGET)

found = []
while True:
    sol = m.solve()
    if sol is None:
        # No further solution. Only "integer infeasible" proves the search is exhausted;
        # anything else (a time limit, an error) leaves the list incomplete.
        if m.solve_details.status != "integer infeasible":
            raise SystemExit(f"enumeration incomplete: {m.solve_details.status}")
        break
    values = [round(sol[t]) for t in take]
    found.append(values)
    # no-good: at least one decision binary must differ from this solution
    m.add_constraint(
        m.sum(1 - take[i] for i in range(len(take)) if values[i] == 1)
        + m.sum(take[i] for i in range(len(take)) if values[i] == 0) >= 1
    )

print(f"Subsets of {NUMBERS} summing to {TARGET}: {len(found)} ({m.solve_details.status})")
for values in found:
    chosen = [n for n, v in zip(NUMBERS, values) if v == 1]
    print(f"  take {chosen}")
