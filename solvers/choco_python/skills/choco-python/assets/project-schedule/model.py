from pychoco.model import Model

# Tasks: (duration, resource use). Precedences: (before, after).
TASKS = [(3, 1), (2, 2), (4, 1), (2, 1)]
PRECEDENCES = [(0, 2), (1, 3)]
CAPACITY = 2
HORIZON = sum(d for d, _ in TASKS)

model = Model()
starts = [model.intvar(0, HORIZON, name=f"start{t}") for t in range(len(TASKS))]
ends = [model.intvar(0, HORIZON, name=f"end{t}") for t in range(len(TASKS))]
tasks = []
for t, (duration, _) in enumerate(TASKS):
    task = model.task(starts[t], duration, ends[t])
    tasks.append(task)
for before, after in PRECEDENCES:
    model.arithm(ends[before], "<=", starts[after]).post()
heights = [model.intvar(use, use, name=f"use{t}") for t, (_, use) in enumerate(TASKS)]
capacity = model.intvar(CAPACITY, CAPACITY, name="capacity")
model.cumulative(tasks, heights, capacity).post()

makespan = model.intvar(0, HORIZON, name="makespan")
model.max(makespan, ends).post()

solution = model.get_solver().find_optimal_solution(makespan, False)
if solution is None:
    print("no schedule")
else:
    for t in range(len(TASKS)):
        print(f"task {t}: start {solution.get_int_val(starts[t])}")
    print("Makespan:", solution.get_int_val(makespan))
