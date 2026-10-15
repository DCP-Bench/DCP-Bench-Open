# Capital budgeting: choose a subset of investments that fits the cash budget and maximises total NPV.
from pyscipopt import Model, quicksum


def build(instance):
    budget = instance["budget"]
    cash_flow = instance["cash_flow"]
    npv = instance["npv"]
    n = len(npv)

    m = Model()

    # x[i] = 1 if investment i is chosen
    x = [m.addVar(name=f"x_{i}", vtype="B") for i in range(n)]
    # total NPV of the chosen investments; bounded by the sum of all NPVs
    z = m.addVar(name="z", vtype="I", lb=0, ub=sum(npv))

    # the sum of all chosen investments must be within the budget
    m.addCons(quicksum(cash_flow[i] * x[i] for i in range(n)) <= budget)

    # total NPV is the sum of the NPVs of the chosen investments
    m.addCons(z == quicksum(npv[i] * x[i] for i in range(n)))

    m.setObjective(z, "maximize")

    return m, {"x": x, "z": z}
