"""Colour the Petersen graph with as few colours as possible, with Z3."""
import z3

N_NODES = 10
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),       # outer cycle
         (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),       # inner star
         (0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]       # spokes

colour = [z3.Int(f"colour_{i}") for i in range(N_NODES)]
# used[v] says whether colour value v appears at all; the colour values need not be contiguous.
used = [z3.Bool(f"used_{v}") for v in range(N_NODES)]

optimizer = z3.Optimize()
for c in colour:
    optimizer.add(c >= 0, c < N_NODES)
for a, b in EDGES:
    optimizer.add(colour[a] != colour[b])
for v in range(N_NODES):
    optimizer.add(used[v] == z3.Or([c == v for c in colour]))
handle = optimizer.minimize(z3.Sum([z3.If(u, 1, 0) for u in used]))

if optimizer.check() != z3.sat:
    raise SystemExit(f"status: {optimizer.check()}")
model = optimizer.model()
values = [model.eval(c, model_completion=True).as_long() for c in colour]
print(f"Colours used: {len(set(values))}")
print(f"proven optimal: {optimizer.lower(handle).as_long() == optimizer.upper(handle).as_long()}")
