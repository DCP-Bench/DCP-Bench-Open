import z3


def build(instance):
    seats, demand = instance["available_seats"], instance["demand"]
    revenue, delta = instance["revenue"], instance["delta"]
    packages, legs = len(demand), len(seats)
    sell = [z3.Int(f"s_{i}") for i in range(packages)]
    constraints = [v >= 0 for v in sell] + [v <= max(demand) for v in sell]
    for j in range(legs):
        constraints.append(z3.Sum([delta[i][j] * sell[i] for i in range(packages)]) <= seats[j])
    constraints += [sell[i] <= demand[i] for i in range(packages)]
    earned = z3.Sum([revenue[i] * sell[i] for i in range(packages)])
    return constraints, {"packages_to_sell": sell, "max_revenue": earned}, ("maximize", earned)
