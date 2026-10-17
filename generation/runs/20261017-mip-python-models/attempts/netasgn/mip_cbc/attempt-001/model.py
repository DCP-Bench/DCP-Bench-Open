# Project assignment problem (netasgn): decide the hours assigned from each person i
# to each project j, minimising the total cost of the assignment.
import mip


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    n_people = len(supply)
    n_projects = len(demand)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the hours assigned from person i to project j, at most its limit Limit_{i, j}
    assign = [
        [
            model.add_var(f"assign_{i}_{j}", lb=0, ub=limit[i][j], var_type=mip.INTEGER)
            for j in range(n_projects)
        ]
        for i in range(n_people)
    ]

    # the total number of hours assigned from each person i equals its supply
    for i in range(n_people):
        model.add_constr(mip.xsum(assign[i][j] for j in range(n_projects)) == supply[i])

    # the total number of hours assigned to each project j equals its demand
    for j in range(n_projects):
        model.add_constr(mip.xsum(assign[i][j] for i in range(n_people)) == demand[j])

    # the total cost is the cost per hour of person i on project j times the hours assigned
    lo = sum(min(0, cost[i][j]) * limit[i][j] for i in range(n_people) for j in range(n_projects))
    hi = sum(max(0, cost[i][j]) * limit[i][j] for i in range(n_people) for j in range(n_projects))
    total_cost = model.add_var("total_cost", lb=lo, ub=hi, var_type=mip.INTEGER)
    model.add_constr(
        total_cost
        == mip.xsum(
            cost[i][j] * assign[i][j]
            for i in range(n_people)
            for j in range(n_projects)
        )
    )

    # the objective is to minimise the total cost
    model.objective = total_cost

    return model, {"assign": assign, "total_cost": total_cost}
