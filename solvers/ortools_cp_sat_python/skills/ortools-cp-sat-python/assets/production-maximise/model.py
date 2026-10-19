"""Maximise: integer production plan for two products under two resource limits."""
from ortools.sat.python import cp_model

model = cp_model.CpModel()
a = model.new_int_var(0, 10, "product_a")
b = model.new_int_var(0, 10, "product_b")

model.add(2 * a + 3 * b <= 12)  # machine hours
model.add(4 * a + b <= 10)      # labour hours
model.maximize(3 * a + 4 * b)   # profit: integer coefficients only

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
print(f"Profit: {int(solver.objective_value)}")
print(f"A={solver.value(a)} B={solver.value(b)}")
