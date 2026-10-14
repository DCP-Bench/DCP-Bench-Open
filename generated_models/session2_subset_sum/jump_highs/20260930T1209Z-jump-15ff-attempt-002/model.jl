# Subset sum: how many bags of each kind were stolen, given the coins per bag of
# each kind and the total number of coins lost.
using JuMP

function build(instance)
    total = instance["total_coins_lost"]
    coins = instance["coin_numbers"]
    n = length(coins)
    model = Model()
    @variable(model, 0 <= bags[1:n] <= total, Int)
    @constraint(model, sum(coins[i] * bags[i] for i in 1:n) == total)
    return model, Dict("bags" => bags)
end
