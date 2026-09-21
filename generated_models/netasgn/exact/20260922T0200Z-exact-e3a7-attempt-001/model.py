# Buy every project its hours from the people who have them, at least cost.
from dcp_pb import Pb


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    people, projects = len(supply), len(demand)

    pb = Pb()
    # 0..10 hours per pairing is the bound the reference declares; the pairing
    # limit narrows it further.
    assign = [[pb.int(0, min(10, limit[i][j])) for j in range(projects)]
              for i in range(people)]
    for i in range(people):
        pb.sum_eq(assign[i], supply[i])
    for j in range(projects):
        pb.sum_eq([assign[i][j] for i in range(people)], demand[j])

    terms = [(cost[i][j], assign[i][j]) for i in range(people) for j in range(projects)]
    ceiling = sum(cost[i][j] * min(10, limit[i][j])
                  for i in range(people) for j in range(projects))
    total = pb.int(0, ceiling)
    pb.eq(terms + [(-1, total)], 0)
    pb.minimise([(1, total)])
    return pb, {"assign": assign, "total_cost": total}
