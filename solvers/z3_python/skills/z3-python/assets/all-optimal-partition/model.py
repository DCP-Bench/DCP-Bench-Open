"""Split jobs over two machines with the smallest possible makespan, then list every optimal split."""
import z3

JOBS = [3, 1, 4, 2, 2]
side = z3.Bools(" ".join(f"side{i}" for i in range(len(JOBS))))  # True: machine 1, False: machine 0


def load(on_machine_one):
    return z3.Sum([z3.If(s == on_machine_one, d, 0) for s, d in zip(side, JOBS)])


load0, load1 = load(False), load(True)
makespan = z3.Int("makespan")
bound = [makespan >= load0, makespan >= load1]  # makespan = max(load0, load1)

# Step 1: prove the optimum.
optimizer = z3.Optimize()
optimizer.add(bound)
handle = optimizer.minimize(makespan)
if optimizer.check() != z3.sat:
    raise SystemExit(f"status: {optimizer.check()}")
best = optimizer.upper(handle).as_long()
assert optimizer.lower(handle).as_long() == best, "optimum not proven"
print(f"Optimal makespan: {best}")

# Step 2: pin the objective at the optimum and enumerate over the decision variables.
solver = z3.Solver()
solver.add(bound + [makespan == best])
count = 0
while solver.check() == z3.sat:
    model = solver.model()
    values = [z3.is_true(model.eval(s, model_completion=True)) for s in side]
    count += 1
    machine_one = [i for i, v in enumerate(values) if v]
    print(f"assignment {count}: jobs {machine_one} on machine 1")
    solver.add(z3.Or([s != v for s, v in zip(side, values)]))

print(f"Optimal assignments: {count}")
