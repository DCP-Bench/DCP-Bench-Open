# Buy every project its hours from the people who have them, at least cost.
from exact import Exact


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    people, projects = len(supply), len(demand)

    solver = Exact()
    # 0..10 hours per pairing is the bound the reference declares; the pairing
    # limit narrows it further.
    assign = [[f"h{i}_{j}" for j in range(projects)] for i in range(people)]
    for i in range(people):
        for j in range(projects):
            solver.addVariable(assign[i][j], 0, min(10, limit[i][j]))
    for i in range(people):
        solver.addConstraint([(1, name) for name in assign[i]],
                             True, supply[i], True, supply[i])
    for j in range(projects):
        solver.addConstraint([(1, assign[i][j]) for i in range(people)],
                             True, demand[j], True, demand[j])

    terms = [(cost[i][j], assign[i][j]) for i in range(people) for j in range(projects)]
    ceiling = sum(cost[i][j] * min(10, limit[i][j])
                  for i in range(people) for j in range(projects))
    solver.addVariable("total", 0, ceiling)
    solver.addConstraint(terms + [(-1, "total")], True, 0, True, 0)
    return (solver, {"assign": assign, "total_cost": "total"},
            ("minimize", [(1, "total")]))
