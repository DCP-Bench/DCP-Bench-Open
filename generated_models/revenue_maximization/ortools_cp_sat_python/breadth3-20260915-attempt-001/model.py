from ortools.sat.python import cp_model


def build(instance):
    seats, demand = instance["available_seats"], instance["demand"]
    revenue, delta = instance["revenue"], instance["delta"]
    packages, legs = len(demand), len(seats)
    model = cp_model.CpModel()
    sell = [model.new_int_var(0, max(demand), f"s_{i}") for i in range(packages)]
    for j in range(legs):
        model.add(sum(delta[i][j] * sell[i] for i in range(packages)) <= seats[j])
    for i in range(packages):
        model.add(sell[i] <= demand[i])
    earned = sum(revenue[i] * sell[i] for i in range(packages))
    model.maximize(earned)
    return model, {"packages_to_sell": sell, "max_revenue": earned}
