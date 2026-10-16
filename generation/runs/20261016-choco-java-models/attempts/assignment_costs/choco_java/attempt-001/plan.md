assignment_costs plan
assign people to 4 tasks with different costs -> x[task][person] Boolean matrix, tasks = rows of cost, people = columns
each task is assigned to exactly one person -> for each task i: sum over j of x[i][j] = 1
it is not necessary to assign all people, but each person takes at most one task -> for each person j: sum over i of x[i][j] <= 1
total cost is minimized -> total = sum of cost[i][j] * x[i][j] (scalar), setObjective MINIMIZE total
objective: minimize
