from pychoco.model import Model

COSTS = [2, 1, 2, 5]
PICK = 2

model = Model()
chosen = [model.boolvar(name=f"item{i}") for i in range(len(COSTS))]
model.sum(chosen, "=", PICK).post()
cost = model.intvar(0, sum(COSTS), name="cost")
model.scalar(chosen, COSTS, "=", cost).post()

solver = model.get_solver()
optimal = solver.find_all_optimal_solutions(cost, False)
print(f"Optimal solutions: {len(optimal)}")
for solution in optimal:
    picks = [i for i, b in enumerate(chosen) if solution.get_int_val(b)]
    print(f"  items {picks} cost {solution.get_int_val(cost)}")
