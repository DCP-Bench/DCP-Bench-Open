# 0/1 knapsack: choose items whose total weight fits the capacity and whose
# total value is as large as possible.
using JuMP

function build(instance)
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = length(values)
    model = Model()
    # x[i] = 1 when item i is taken
    @variable(model, x[1:n], Bin)
    # the taken items fit into the knapsack
    @constraint(model, sum(weights[i] * x[i] for i in 1:n) <= capacity)
    # the value of the taken items is as large as possible
    @objective(model, Max, sum(values[i] * x[i] for i in 1:n))
    return model, Dict("x" => x)
end
