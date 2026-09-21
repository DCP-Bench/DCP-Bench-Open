# Buy every project its hours from the people who have them, at least cost.
from dcp_maxsat import MaxSat


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    people, projects = len(supply), len(demand)

    sat = MaxSat()
    # Hours from one person to one project cannot exceed that pairing's limit,
    # nor the person's supply.
    assign = [[sat.int(0, min(limit[i][j], supply[i])) for j in range(projects)]
              for i in range(people)]
    for i in range(people):
        sat.sum_eq(assign[i], supply[i])
    for j in range(projects):
        sat.sum_eq([assign[i][j] for i in range(people)], demand[j])

    terms = [(cost[i][j], assign[i][j]) for i in range(people) for j in range(projects)]
    ceiling = sum(cost[i][j] * min(limit[i][j], supply[i])
                  for i in range(people) for j in range(projects))
    total = sat.int(0, ceiling)
    sat.link_sum(terms, total)
    return sat, {"assign": assign, "total_cost": total}, ("minimize", total)
