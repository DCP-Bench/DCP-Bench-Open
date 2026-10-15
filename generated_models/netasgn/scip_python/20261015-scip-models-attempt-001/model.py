from pyscipopt import Model, quicksum

# Project assignment: assign hours from people to projects at minimum total cost,
# so that each person's supply is used up and each project's demand is met exactly.
def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    P = range(len(supply))
    J = range(len(demand))

    m = Model()

    # x[i, j] = hours person i works on project j; bounded by the per-pair limit
    x = {}
    for i in P:
        for j in J:
            x[i, j] = m.addVar(name=f"x_{i}_{j}", vtype="I", lb=0,
                               ub=min(limit[i][j], supply[i], demand[j]))

    # the total hours assigned from each person equals its supply
    for i in P:
        m.addCons(quicksum(x[i, j] for j in J) == supply[i], name=f"supply_{i}")

    # the total hours assigned to each project equals its demand
    for j in J:
        m.addCons(quicksum(x[i, j] for i in P) == demand[j], name=f"demand_{j}")

    # total cost: cost per hour of person i on project j times hours assigned
    total_cost = m.addVar(name="total_cost", vtype="I", lb=0)
    m.addCons(total_cost == quicksum(cost[i][j] * x[i, j] for i in P for j in J),
              name="total_cost_def")
    m.setObjective(total_cost, "minimize")

    assign = [[x[i, j] for j in J] for i in P]
    return m, {"assign": assign, "total_cost": total_cost}
