"""Rent vans and minibuses for a group, at the lowest total cost, with Z3."""
import z3

GROUP_SIZE = 10
VAN = {"seats": 4, "cost": 3}
MINIBUS = {"seats": 8, "cost": 5}
MAX_MINIBUSES = 2

vans, minibuses = z3.Ints("vans minibuses")
optimizer = z3.Optimize()
optimizer.add(vans >= 0, minibuses >= 0, minibuses <= MAX_MINIBUSES)
optimizer.add(VAN["seats"] * vans + MINIBUS["seats"] * minibuses >= GROUP_SIZE)
cost = VAN["cost"] * vans + MINIBUS["cost"] * minibuses
handle = optimizer.minimize(cost)

if optimizer.check() != z3.sat:
    raise SystemExit(f"status: {optimizer.check()}")
model = optimizer.model()
print(f"vans: {model[vans]}, minibuses: {model[minibuses]}")
print(f"Minimum cost: {optimizer.upper(handle)}")
print(f"proven optimal: {optimizer.lower(handle).as_long() == optimizer.upper(handle).as_long()}")
