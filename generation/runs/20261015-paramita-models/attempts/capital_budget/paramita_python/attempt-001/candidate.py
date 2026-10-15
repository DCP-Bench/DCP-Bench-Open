"""Capital budgeting: choose investments to maximise total NPV within a cash budget.

Each investment is a Bool: chosen or not. The budget and the NPV total are
weighted sums of these Bools, so no integer encoding is needed.
"""
from paramita.modelling import Bool


def build(instance):
    budget = instance["budget"]
    cash_flow = instance["cash_flow"]
    npv = instance["npv"]
    n = len(npv)

    # x[i] is true when investment i is chosen
    x = [Bool(f"x_{i}") for i in range(n)]

    cons = []
    # the sum of all chosen investments' cash outflows must not exceed the total budget
    cons.append(sum(cash_flow[i] * x[i] for i in range(n)) <= budget)

    # total NPV of the chosen investments (objective and output)
    z = sum(npv[i] * x[i] for i in range(n))

    return cons, {"x": x, "z": z}, ("maximize", z)
