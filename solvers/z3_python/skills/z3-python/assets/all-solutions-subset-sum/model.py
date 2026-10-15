"""Enumerate every subset of weights that sums to a target, with Z3."""
import z3

WEIGHTS = [2, 3, 4, 5, 6]
TARGET = 9

take = z3.Bools(" ".join(f"take{i}" for i in range(len(WEIGHTS))))
total = z3.Int("total")  # auxiliary: determined by take, so it must not be blocked

solver = z3.Solver()
solver.add(total == z3.Sum([z3.If(t, w, 0) for t, w in zip(take, WEIGHTS)]))
solver.add(total == TARGET)

subsets = []
while solver.check() == z3.sat:
    model = solver.model()
    values = [z3.is_true(model.eval(t, model_completion=True)) for t in take]
    subsets.append([w for v, w in zip(values, WEIGHTS) if v])
    # Block this assignment of the declared variables only, so each subset appears once.
    solver.add(z3.Or([t != v for t, v in zip(take, values)]))

for number, subset in enumerate(sorted(subsets), 1):
    print(f"solution {number}: {subset}")
print(f"Solutions: {len(subsets)}")
