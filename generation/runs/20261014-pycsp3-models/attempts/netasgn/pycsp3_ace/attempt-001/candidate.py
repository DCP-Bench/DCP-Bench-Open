from pycsp3 import *

# assign the hours of the people to the projects at the least total cost
n_people = len(data.supply)
n_projects = len(data.demand)
largest_limit = max(max(row) for row in data.limit)
largest_cost = max(max(row) for row in data.cost)
# assign[i][j] is the number of hours person i works on project j
assign = VarArray(size=[n_people, n_projects], dom=range(0, largest_limit + 1))
# the total cost of the assignment
total_cost = Var(dom=range(0, largest_cost * sum(data.supply) + 1))
satisfy(
    # a person contributes at most the limit to each project
    [assign[i][j] <= data.limit[i][j] for i in range(n_people) for j in range(n_projects)],
    # the total hours of each person equal the person's supply
    [Sum(assign[i]) == data.supply[i] for i in range(n_people)],
    # the total hours on each project equal the project's demand
    [Sum(assign[:, j]) == data.demand[j] for j in range(n_projects)],
    # the total cost is the cost per hour times the hours of each assignment
    total_cost == Sum(data.cost[i][j] * assign[i][j] for i in range(n_people) for j in range(n_projects)),
)
# minimise the total cost of assigning the people to the projects
minimize(total_cost)
