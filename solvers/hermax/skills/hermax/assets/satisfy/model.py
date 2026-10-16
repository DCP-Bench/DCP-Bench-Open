# Split 1..8 into two groups of four with equal sums.
from hermax.model import Model

VALUES = list(range(1, 9))
HALF = sum(VALUES) // 2

m = Model()
in_a = m.bool_vector("in_a", len(VALUES))  # True: the value goes to group A

m &= (sum(in_a[i] for i in range(len(VALUES))) == len(VALUES) // 2)
m &= (sum(v * in_a[i] for i, v in enumerate(VALUES)) == HALF)

r = m.solve()
if r.status != "sat":
    raise SystemExit(f"status: {r.status}")

group_a = [v for v, chosen in zip(VALUES, r[in_a]) if chosen]
group_b = [v for v in VALUES if v not in group_a]
print("A:", group_a, "B:", group_b)
print(f"A sums to {sum(group_a)}, B sums to {sum(group_b)}")
