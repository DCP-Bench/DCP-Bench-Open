"""Schedule tasks one after another on a single machine, respecting release times and precedences."""
import z3

# name: (duration, release time)
TASKS = {"cut": (3, 0), "weld": (2, 2), "paint": (4, 0), "dry": (2, 0)}
PRECEDENCES = [("cut", "paint"), ("weld", "dry")]  # first must finish before second starts

names = list(TASKS)
start = {n: z3.Int(f"start_{n}") for n in names}
end = {n: start[n] + TASKS[n][0] for n in names}
makespan = z3.Int("makespan")

optimizer = z3.Optimize()
for n in names:
    optimizer.add(start[n] >= TASKS[n][1])
    optimizer.add(makespan >= end[n])
# No overlap on one machine: for every pair, one finishes before the other starts.
for i, a in enumerate(names):
    for b in names[i + 1:]:
        optimizer.add(z3.Or(end[a] <= start[b], end[b] <= start[a]))
for before, after in PRECEDENCES:
    optimizer.add(end[before] <= start[after])
handle = optimizer.minimize(makespan)

if optimizer.check() != z3.sat:
    raise SystemExit(f"status: {optimizer.check()}")
model = optimizer.model()
for n in sorted(names, key=lambda n: model.eval(start[n]).as_long()):
    s = model.eval(start[n]).as_long()
    print(f"{n:6s} starts {s:2d} ends {s + TASKS[n][0]:2d}")
print(f"Minimum makespan: {optimizer.upper(handle)}")
print(f"proven optimal: {optimizer.lower(handle).as_long() == optimizer.upper(handle).as_long()}")
