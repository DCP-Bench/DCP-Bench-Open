from pychoco.model import Model

TASKS = 5
SLOTS = 4  # fewer slots than tasks: no assignment can give every task its own slot

model = Model()
slot = [model.intvar(0, SLOTS - 1, name=f"task{t}") for t in range(TASKS)]
model.all_different(slot).post()

solution = model.get_solver().find_solution()
if solution is None:
    print(f"No assignment of {TASKS} tasks to {SLOTS} slots: infeasible")
else:
    print("Assignment:", [solution.get_int_val(s) for s in slot])
