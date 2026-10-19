from pychoco.model import Model

# Three tasks on one machine: they may not overlap in time.
DURATIONS = [2, 3, 1]
PRECEDENCES = [(0, 2)]  # task 0 finishes before task 2 starts

model = Model()
horizon = sum(DURATIONS)
start = [model.intvar(0, horizon, name=f"s{t}") for t in range(len(DURATIONS))]
end = [model.intvar(0, horizon, name=f"e{t}") for t in range(len(DURATIONS))]
tasks = [model.task(start[t], DURATIONS[t], end[t]) for t in range(len(DURATIONS))]

# No overlap on one machine = cumulative with unit height per task and capacity 1.
# Heights and capacity must be IntVars: a plain int raises AttributeError.
heights = [model.intvar(1, 1) for _ in tasks]
model.cumulative(tasks, heights, model.intvar(1, 1)).post()

for before, after in PRECEDENCES:
    model.arithm(end[before], "<=", start[after]).post()

makespan = model.intvar(0, horizon, name="makespan")
model.max(makespan, end).post()

solution = model.get_solver().find_optimal_solution(makespan, False)
if solution is None:
    print("no schedule")
else:
    for t in range(len(DURATIONS)):
        print(f"task {t}: {solution.get_int_val(start[t])} to {solution.get_int_val(end[t])}")
    print("Makespan:", solution.get_int_val(makespan))
