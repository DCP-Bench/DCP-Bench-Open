# Maximum-weight independent set: pick vertices with the largest total weight,
# no two adjacent.
from hermax.model import Model

WEIGHT = [5, 3, 8, 2, 7, 4]
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)]

m = Model()
pick = m.bool_vector("pick", len(WEIGHT))
for u, v in EDGES:
    m &= (~pick[u] | ~pick[v])   # adjacent vertices are not both picked

# The solver minimises the weight of the soft clauses it breaks. Paying w for each
# vertex left out makes the broken weight equal to the weight forgone.
for i, w in enumerate(WEIGHT):
    m.obj[w] += pick[i]

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
best = sum(WEIGHT) - r.cost
chosen = [i for i in range(len(WEIGHT)) if r[pick[i]]]
print("picked:", chosen)
print(f"best weight {best}")
