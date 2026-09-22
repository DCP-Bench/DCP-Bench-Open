# Choose investments to maximise net present value within the budget.
from exact import Exact


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    budget = instance["budget"]
    n = len(npv)

    solver = Exact()
    x = [f"x{j}" for j in range(n)]
    for name in x:
        solver.addVariable(name, 0, 1)
    solver.addConstraint(list(zip(cash_flow, x)), False, 0, True, budget)

    # The brief declares the total as an output, so it needs a variable of its
    # own. Exact integers are native, so the wide range costs nothing.
    solver.addVariable("z", 0, sum(npv))
    solver.addConstraint(list(zip(npv, x)) + [(-1, "z")], True, 0, True, 0)
    return solver, {"x": x, "z": "z"}, ("maximize", [(1, "z")])
