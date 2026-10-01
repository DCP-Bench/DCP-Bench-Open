# Covering (OPL): hire a set of workers at the least total hiring cost so that
# every task is performed by at least one hired worker who is qualified for it.
using JuMP

function build(instance)
    nb_workers = instance["nb_workers"]
    cost = instance["Cost"]                  # hiring cost of each worker
    qualified = instance["Qualified"]        # qualified[t] = the (1-based) workers able to do task t
    num_tasks = length(qualified)

    model = Model()

    # workers[w] = 1 when worker w is hired
    @variable(model, workers[1:nb_workers], Bin)

    # total_cost = the sum of the hiring costs of the hired workers, a declared output;
    # it cannot exceed the cost of hiring everyone
    @variable(model, 0 <= total_cost <= sum(cost), Int)
    @constraint(model, total_cost == sum(cost[w] * workers[w] for w in 1:nb_workers))

    # every task has at least one hired worker who is qualified for it
    @constraint(model, [t = 1:num_tasks], sum(workers[w] for w in qualified[t]) >= 1)

    @objective(model, Min, total_cost)
    return model, Dict("total_cost" => total_cost, "workers" => workers)
end
