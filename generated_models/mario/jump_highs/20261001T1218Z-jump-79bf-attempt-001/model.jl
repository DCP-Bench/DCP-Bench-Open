# Mario: collect as much gold as possible by visiting houses. Mario starts at his own house
# and ends at Luigi's house; travelling between houses uses fuel and Mario has a limited
# amount. The route is described by the successor of each house; a house that is not on
# the route is its own successor, and Luigi's house leads back to Mario's.
using JuMP

function build(instance)
    n = instance["nHouses"]
    mario = instance["marioHouse"] + 1      # 1-based house numbers here
    luigi = instance["luigiHouse"] + 1
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]         # arc_fuel[i][j] = fuel to go from house i to house j
    gold = instance["goldInHouse"]          # gold in each house

    model = Model()

    # next_is[i, j] = 1 when the successor of house i is house j; next_is[i, i] = 1 means
    # house i is not on the route
    @variable(model, next_is[1:n, 1:n], Bin)

    # Every house has exactly one successor, and all successors are different (every house
    # is the successor of exactly one house, itself included)
    @constraint(model, [i = 1:n], sum(next_is[i, j] for j in 1:n) == 1)
    @constraint(model, [j = 1:n], sum(next_is[i, j] for i in 1:n) == 1)

    # The route ends at Luigi's house, which leads back to Mario's house
    @constraint(model, next_is[luigi, mario] == 1)

    # The houses on the route form one path from Mario's house to Luigi's house (no separate
    # loops). rank[i] is the position of house i on the route; following a route arc other
    # than the closing one back to Mario raises the rank by at least one (the big-M n is
    # the largest rank difference plus one). Houses that are not on the route are free.
    @variable(model, 1 <= rank[1:n] <= n, Int)
    @constraint(model, rank[mario] == 1)
    for i in 1:n, j in 1:n
        if i != j && j != mario
            @constraint(model, rank[j] >= rank[i] + 1 - n * (1 - next_is[i, j]))
        end
    end

    # Fuel used by the route may not exceed the limit
    @constraint(model, sum(arc_fuel[i][j] * next_is[i, j] for i in 1:n, j in 1:n) <= fuel_limit)

    # Maximise the gold collected in the houses on the route (those that are not their own
    # successor)
    @objective(model, Max, sum(gold[i] * (1 - next_is[i, i]) for i in 1:n))

    # s[i] = the (0-based) house that follows house i (declared output)
    s = [sum((j - 1) * next_is[i, j] for j in 1:n) for i in 1:n]
    return model, Dict("s" => s)
end
