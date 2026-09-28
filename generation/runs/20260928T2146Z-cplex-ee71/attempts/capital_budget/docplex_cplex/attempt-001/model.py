"""Capital budgeting: choose investments within the budget to maximise the total net present value."""
from docplex.mp.model import Model


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    investments = range(len(npv))

    model = Model("capital_budget")

    # x[i] is 1 when investment i is chosen.
    x = model.binary_var_list(len(npv), name="x")

    # The cash outflow of the chosen investments stays within the budget.
    model.add_constraint(model.dot(x, cash_flow) <= instance["budget"], ctname="budget")

    # z is the total NPV of the chosen investments, and it is maximised.
    z = model.dot(x, npv)
    model.maximize(z)

    return model, {"x": [x[i] for i in investments], "z": z}
