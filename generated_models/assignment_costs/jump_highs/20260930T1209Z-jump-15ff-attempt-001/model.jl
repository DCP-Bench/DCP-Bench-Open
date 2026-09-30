# Assignment: give each task to one person, no person more than one task, at
# the least total cost. Not every person needs a task.
using JuMP

function build(instance)
    cost = instance["cost"]      # cost[task][person]
    rows = length(cost)
    cols = length(cost[1])
    model = Model()
    # x[i, j] = 1 when task i goes to person j
    @variable(model, x[1:rows, 1:cols], Bin)
    # every task is assigned exactly once
    @constraint(model, [i = 1:rows], sum(x[i, j] for j in 1:cols) == 1)
    # a person takes at most one task
    @constraint(model, [j = 1:cols], sum(x[i, j] for i in 1:rows) <= 1)
    @objective(model, Min, sum(cost[i][j] * x[i, j] for i in 1:rows, j in 1:cols))
    return model, Dict("x" => x)
end
