import cpmpy as cp


def build(instance):
    seats, demand = instance["available_seats"], instance["demand"]
    revenue, delta = instance["revenue"], instance["delta"]
    packages, legs = len(demand), len(seats)
    sell = cp.intvar(0, max(demand), shape=packages, name="packages_to_sell")
    model = cp.Model()
    for j in range(legs):
        model += cp.sum([delta[i][j] * sell[i] for i in range(packages)]) <= seats[j]
    for i in range(packages):
        model += sell[i] <= demand[i]
    earned = cp.sum([revenue[i] * sell[i] for i in range(packages)])
    model.maximize(earned)
    return model, {"packages_to_sell": [sell[i] for i in range(packages)], "max_revenue": earned}
