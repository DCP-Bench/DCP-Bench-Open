"""Maximise: integer production plan that maximises profit under resource limits."""
from docplex.mp.model import Model

PRODUCTS = ["chairs", "tables"]
PROFIT = [5, 4]
USE = {  # resource -> units used per product, and the available amount
    "wood": ([6, 4], 24),
    "labour": ([1, 2], 6),
}

m = Model(name="product-mix")
make = m.integer_var_list(len(PRODUCTS), lb=0, name="make")  # whole units only

for resource, (per_unit, available) in USE.items():
    m.add_constraint(m.scal_prod(make, per_unit) <= available, ctname=f"cap_{resource}")

m.maximize(m.scal_prod(make, PROFIT))
sol = m.solve()
if sol is None:
    raise SystemExit(f"no plan: {m.solve_details.status}")

print(f"Best profit: {sol.objective_value:.0f} ({m.solve_details.status})")
for name, var in zip(PRODUCTS, make):
    print(f"  make {sol[var]:.0f} {name}")
