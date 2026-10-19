"""All optimal solutions: pick 2 of 4 items with the largest total value (several ties)."""
from ortools.sat.python import cp_model

VALUES = [3, 3, 3, 1]
PICK = 2

model = cp_model.CpModel()
take = [model.new_bool_var(f"take{i}") for i in range(len(VALUES))]
model.add(sum(take) == PICK)
total = sum(v * t for v, t in zip(VALUES, take))
model.maximize(total)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status != cp_model.OPTIMAL:
    raise SystemExit(f"no optimum: {solver.status_name(status)}")
best = int(solver.objective_value)
print(f"Optimal value: {best}")

# Fix the objective at the optimum and drop it: with an objective still set,
# enumerate_all_solutions returns only one solution.
model.add(total == best)
model.clear_objective()


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append(tuple(self.value(t) for t in take))


enumerator = cp_model.CpSolver()
enumerator.parameters.enumerate_all_solutions = True
collector = Collect()
enumerator.solve(model, collector)

print(f"Optimal solutions: {len(collector.solutions)}")
for solution in sorted(collector.solutions):
    print("take", solution)
