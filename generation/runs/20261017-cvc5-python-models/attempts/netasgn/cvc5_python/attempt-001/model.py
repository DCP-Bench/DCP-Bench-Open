# Project assignment problem (netasgn), cvc5 model.
# Assign hours assign[i][j] from person i to project j, minimising total cost.

import cvc5.pythonic as cz


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    n_people = len(supply)
    n_projects = len(demand)

    x = [[cz.Int(f"x_{i}_{j}") for j in range(n_projects)] for i in range(n_people)]

    constraints = []

    # Each assignment is between 0 and its limit, as stated in the description.
    # Limit i, j bounds the hours person i can contribute to project j.
    for i in range(n_people):
        for j in range(n_projects):
            constraints.append(x[i][j] >= 0)
            constraints.append(x[i][j] <= limit[i][j])

    # The total number of hours assigned from each person i equals its supply.
    for i in range(n_people):
        constraints.append(cz.Sum([x[i][j] for j in range(n_projects)]) == supply[i])

    # The total number of hours assigned to each project j equals its demand.
    for j in range(n_projects):
        constraints.append(cz.Sum([x[i][j] for i in range(n_people)]) == demand[j])

    # Total cost is the sum of cost per hour times hours assigned.
    total_cost = cz.Sum([cost[i][j] * x[i][j] for i in range(n_people) for j in range(n_projects)])

    outputs = {
        "assign": [[x[i][j] for j in range(n_projects)] for i in range(n_people)],
        "total_cost": total_cost,
    }
    return constraints, outputs, ("minimize", total_cost)
