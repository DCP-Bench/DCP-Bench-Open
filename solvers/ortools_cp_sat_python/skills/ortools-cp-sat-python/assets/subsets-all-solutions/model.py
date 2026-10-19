"""All solutions: choose exactly K of the numbers 1..N whose sum is T."""
from ortools.sat.python import cp_model

N, K, T = 6, 3, 10

model = cp_model.CpModel()
pick = [model.new_bool_var(f"pick{i}") for i in range(1, N + 1)]
model.add(sum(pick) == K)
model.add(sum(i * p for i, p in zip(range(1, N + 1), pick)) == T)


class Collect(cp_model.CpSolverSolutionCallback):
    """Called once per solution. Records only the picked numbers, not every variable."""

    def __init__(self):
        super().__init__()
        self.subsets = []

    def on_solution_callback(self):
        self.subsets.append([i for i, p in zip(range(1, N + 1), pick) if self.value(p)])


solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
collector = Collect()
status = solver.solve(model, collector)

print(solver.status_name(status))
print(f"Solutions: {len(collector.subsets)}")
for subset in collector.subsets:
    print(subset)
