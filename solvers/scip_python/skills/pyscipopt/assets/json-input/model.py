# Graph colouring read from JSON: colour the vertices with as few colours as possible
# so that neighbours differ. Usage: python model.py [data.json]
# The data file holds "n" and a ragged "neighbours" list (one list per vertex); any other
# key ("name", "note") is ignored. json is in Python's standard library.
import json
import sys

from pyscipopt import Model, quicksum

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    data = json.load(f)
n = data["n"]
neighbours = data["neighbours"]           # ragged: each vertex has its own list
edges = {(min(u, v), max(u, v)) for u in range(n) for v in neighbours[u] if u != v}
k = n                                     # at most n colours are ever needed

m = Model("colouring")
m.hideOutput()
x = {(v, c): m.addVar(vtype="B", name=f"x_{v}_{c}") for v in range(n) for c in range(k)}
used = [m.addVar(vtype="B", name=f"used_{c}") for c in range(k)]
for v in range(n):
    m.addCons(quicksum(x[v, c] for c in range(k)) == 1)   # one colour per vertex
    for c in range(k):
        m.addCons(x[v, c] <= used[c])                     # every vertex, isolated ones too, counts its colour
for u, v in edges:
    for c in range(k):
        m.addCons(x[u, c] + x[v, c] <= used[c])           # neighbours differ; c counts as used
for c in range(1, k):
    m.addCons(used[c] <= used[c - 1])                     # symmetry: use colours 0, 1, ... in order
colours = m.addVar(vtype="I", lb=1, ub=k, name="colours")
m.addCons(colours == quicksum(used))
m.setObjective(colours, "minimize")

m.optimize()
status = m.getStatus()
print("Status:", status)
if status == "optimal":
    print("Colours:", round(m.getVal(colours)))
    print("Colouring:", [next(c for c in range(k) if m.getVal(x[v, c]) > 0.5) for v in range(n)])
