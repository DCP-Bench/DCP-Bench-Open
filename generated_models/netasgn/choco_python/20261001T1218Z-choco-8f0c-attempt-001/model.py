# Network assignment: decide how many hours each person works on each project so that
# every person uses exactly their available hours, every project gets exactly the
# hours it demands, no person exceeds their limit on a project, and the total cost
# of the hours is as small as possible.
from pychoco.model import Model

# Upper bound the reference declares on the hours of one person on one project
# (it belongs to the problem, not the instance).
MAX_HOURS = 10


def build(instance):
    supply = instance["supply"]  # supply[i] = hours person i has available
    demand = instance["demand"]  # demand[j] = hours project j requires
    cost = instance["cost"]  # cost[i][j] = cost per hour of person i on project j
    limit = instance["limit"]  # limit[i][j] = most hours person i may work on project j
    num_people = len(supply)
    num_projects = len(demand)

    model = Model()

    # assign[i][j] = hours person i works on project j
    assign = [[model.intvar(0, MAX_HOURS, name=f"assign_{i}_{j}") for j in range(num_projects)]
              for i in range(num_people)]

    # the hours a person gives to all projects add up to their supply
    for i in range(num_people):
        model.sum(assign[i], "=", supply[i]).post()

    # the hours a project receives from all people add up to its demand
    for j in range(num_projects):
        model.sum([assign[i][j] for i in range(num_people)], "=", demand[j]).post()

    # a person cannot work more than their limit on a project
    for i in range(num_people):
        for j in range(num_projects):
            model.arithm(assign[i][j], "<=", limit[i][j]).post()

    # total cost of all hours (Choco minimises one variable, so it gets its own);
    # it is at most the cost of MAX_HOURS hours in every cell
    flat_assign = [assign[i][j] for i in range(num_people) for j in range(num_projects)]
    flat_cost = [cost[i][j] for i in range(num_people) for j in range(num_projects)]
    total_cost = model.intvar(0, MAX_HOURS * sum(flat_cost), name="total_cost")
    model.scalar(flat_assign, flat_cost, "=", total_cost).post()

    return model, {"assign": assign, "total_cost": total_cost}, ("minimize", total_cost)
