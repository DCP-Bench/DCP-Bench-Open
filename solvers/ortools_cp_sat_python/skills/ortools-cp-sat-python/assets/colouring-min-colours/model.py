"""Graph colouring: colour the nodes so adjacent nodes differ, using as few colours as possible."""
from ortools.sat.python import cp_model

N_NODES = 4
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]

model = cp_model.CpModel()
colour = [model.new_int_var(0, N_NODES - 1, f"colour{i}") for i in range(N_NODES)]
for u, v in EDGES:
    model.add(colour[u] != colour[v])

# Minimise the largest colour index. At the optimum the colours are 0..k-1 with k
# the number of colours used, so the largest index is k - 1 and minimising it
# minimises the number of distinct colours.
largest = model.new_int_var(0, N_NODES - 1, "largest")
model.add_max_equality(largest, colour)
model.minimize(largest)

solver = cp_model.CpSolver()
status = solver.solve(model)
print(solver.status_name(status))
if status == cp_model.OPTIMAL:
    values = [solver.value(c) for c in colour]
    print(f"Colours used: {len(set(values))}")
    print(f"Colour per node: {values}")
