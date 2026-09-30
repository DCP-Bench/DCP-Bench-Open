# Coins: how many coins of each denomination to carry, as few as possible, so
# that every amount from 1 up to (not including) the maximum can be paid exactly.
using JuMP

function build(instance)
    denominations = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]   # the largest amount is one less
    n = length(denominations)
    model = Model()
    # x[i] = the coins of denomination i carried
    @variable(model, 0 <= x[1:n] <= max_amount, Int)
    # used[a, i] = the coins of denomination i used to pay the amount a; a payment
    # uses no more coins of a kind than are carried, and adds up to the amount
    @variable(model, 0 <= used[1:max_amount-1, 1:n] <= max_amount, Int)
    @constraint(model, [a = 1:max_amount-1, i = 1:n], used[a, i] <= x[i])
    @constraint(model, [a = 1:max_amount-1], sum(denominations[i] * used[a, i] for i in 1:n) == a)
    @objective(model, Min, sum(x))
    return model, Dict("x" => x)
end
