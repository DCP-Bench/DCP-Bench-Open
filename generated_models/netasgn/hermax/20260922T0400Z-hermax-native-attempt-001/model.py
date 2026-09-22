# Buy every project its hours from the people who have them, at least cost.
from hermax.model import Model


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    people, projects = len(supply), len(demand)

    m = Model()
    # Hours from one person to one project cannot exceed that pairing's limit,
    # nor the person's supply.
    assign = [[m.int(f"assign_{i}_{j}", 0, min(limit[i][j], supply[i]))
               for j in range(projects)] for i in range(people)]
    for i in range(people):
        m &= (sum(assign[i][j] for j in range(projects)) == supply[i])
    for j in range(projects):
        m &= (sum(assign[i][j] for i in range(people)) == demand[j])

    ceiling = sum(cost[i][j] * min(limit[i][j], supply[i])
                  for i in range(people) for j in range(projects))
    total = m.int("total_cost", 0, ceiling)
    m &= (sum(cost[i][j] * assign[i][j]
              for i in range(people) for j in range(projects)) == total)
    m.obj += total
    return m, {"assign": assign, "total_cost": total}
