"""Minimise colours: colour the Petersen graph with as few colours as possible.

Each node takes exactly one colour. Two adjacent nodes may not share a colour. A
colour counts as used when some node takes it, so the objective is the sum of the
used-colour variables.
"""
from exact import Exact

N = 10
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7), (3, 8),
         (4, 9), (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
K = N  # one colour per node is always enough

solver = Exact()
# x[v][k] == 1 exactly when node v takes colour k (one-hot indicators)
x = [[f"x_{v}_{k}" for k in range(K)] for v in range(N)]
used = [f"used_{k}" for k in range(K)]

for v in range(N):
    for k in range(K):
        solver.addVariable(x[v][k], 0, 1)
    solver.addConstraint([(1, x[v][k]) for k in range(K)], True, 1, True, 1)

for k in range(K):
    solver.addVariable(used[k], 0, 1)
    # a node with colour k forces used_k to 1: x[v][k] <= used_k
    for v in range(N):
        solver.addConstraint([(1, x[v][k]), (-1, used[k])], False, 0, True, 0)

for a, b in EDGES:
    for k in range(K):
        solver.addConstraint([(1, x[a][k]), (1, x[b][k])], False, 0, True, 1)

solver.setObjective([(1, used[k]) for k in range(K)], minimize=True)
state, value = solver.toOptimum()
print("status:", state)
if state == "SAT":
    flat = [x[v][k] for v in range(N) for k in range(K)]
    vals = solver.getLastSolutionFor(flat)
    colour = [next(k for k in range(K) if vals[v * K + k] == 1) for v in range(N)]
    print("colours used:", value)
    print("node colours:", colour)
    print("proper colouring:", all(colour[a] != colour[b] for a, b in EDGES))
