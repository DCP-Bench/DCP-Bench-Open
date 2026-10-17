# Problem: capital_budget
# A company is considering a number of investments. Each investment will yield a net
# present value (NPV). Each investment requires a certain cash outflow at the present
# time. There is a total budget available for investment. How to maximize the NPV
# obtained from the investments?
# Print whether each investment is chosen (x) as a list of booleans, and the total
# NPV (z) as an integer.

import cvc5.pythonic as cz


def build(instance):
    budget = instance["budget"]
    cash_flow = instance["cash_flow"]
    npv = instance["npv"]
    n = len(npv)

    x = [cz.Bool(f"x_{i}") for i in range(n)]

    constraints = []

    # There is a total budget available for investment: the cash outflow of the chosen
    # investments does not exceed the budget.
    total_cash = cz.Sum([cz.If(x[i], cash_flow[i], 0) for i in range(n)])
    constraints.append(total_cash <= budget)

    # The total NPV is the sum of the NPVs of the chosen investments.
    z = cz.Sum([cz.If(x[i], npv[i], 0) for i in range(n)])

    return constraints, {"x": x, "z": z}, ("maximize", z)
