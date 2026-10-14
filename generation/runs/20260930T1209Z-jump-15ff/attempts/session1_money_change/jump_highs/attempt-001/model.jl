# Money change: pay the amount with the available coins using as few coins as
# possible.
using JuMP

function build(instance)
    amount = instance["amount"]
    types = instance["types_of_coins"]        # value of each type of coin
    available = instance["available_coins"]   # coins of each type available
    n = length(types)
    model = Model()
    @variable(model, 0 <= counts[i = 1:n] <= available[i], Int)
    @constraint(model, sum(types[i] * counts[i] for i in 1:n) == amount)
    @objective(model, Min, sum(counts))
    return model, Dict("coin_counts" => counts)
end
