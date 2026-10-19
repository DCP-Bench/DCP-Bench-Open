# Four tasks on one shared resource of capacity 2, with precedences. Minimise the makespan.
from hermax.model import Model

NAMES = ["A", "B", "C", "D"]
DURATION = [3, 2, 4, 2]
DEMAND = [1, 1, 2, 1]        # resource units each task uses while it runs
CAPACITY = 2
PRECEDES = [(0, 2), (1, 3)]  # (a, b): task a must finish before task b starts
HORIZON = sum(DURATION)

m = Model()
start = m.int_vector("start", len(NAMES), 0, HORIZON)
makespan = m.int("makespan", 0, HORIZON)

for i, d in enumerate(DURATION):
    m &= (start[i] + d <= makespan)
for a, b in PRECEDES:
    m &= (start[a] + DURATION[a] <= start[b])
m.cumulative(start, DURATION, DEMAND, CAPACITY)  # adds its constraint itself
m.obj += makespan

r = m.solve()
if r.status != "optimum":
    raise SystemExit(f"status: {r.status}")
for i, name in enumerate(NAMES):
    print(f"{name}: starts {r[start[i]]}, runs {DURATION[i]}")
print(f"Makespan: {r.cost}")
