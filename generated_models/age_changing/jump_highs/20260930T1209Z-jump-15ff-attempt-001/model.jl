# Age changing: applying +2, /8, -3 and *7 to my age in some order gives my
# husband's age, and applying them to his age in a different order gives mine.
# Ages are 16 to 120.
using JuMP

function build(instance)
    # The puzzle has no data.
    n = 4
    model = Model()
    @variable(model, 16 <= m <= 120, Int)   # my age
    @variable(model, 16 <= h <= 120, Int)   # my husband's age
    # op[s, i, k] = 1 when step i of order s applies operation k: +2, /8, -3, *7
    @variable(model, op[1:2, 1:n, 1:n], Bin)
    @constraint(model, [s = 1:2, i = 1:n], sum(op[s, i, :]) == 1)
    @constraint(model, [s = 1:2, k = 1:n], sum(op[s, :, k]) == 1)
    # the two orders differ somewhere: they do not agree on all four steps
    @variable(model, same[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, k = 1:n], same[i, k] >= op[1, i, k] + op[2, i, k] - 1)
    @constraint(model, sum(same) <= n - 1)
    # value[s, i] = the age after i - 1 steps of order s: order 1 goes from my age
    # to his, order 2 from his to mine
    @variable(model, 1 <= value[1:2, 1:n+1] <= 1000, Int)
    @constraint(model, value[1, 1] == m)
    @constraint(model, value[1, n + 1] == h)
    @constraint(model, value[2, 1] == h)
    @constraint(model, value[2, n + 1] == m)
    for s in 1:2, i in 1:n
        old, new = value[s, i], value[s, i + 1]
        @constraint(model, op[s, i, 1] --> {new == old + 2})
        @constraint(model, op[s, i, 2] --> {8 * new == old})
        @constraint(model, op[s, i, 3] --> {new == old - 3})
        @constraint(model, op[s, i, 4] --> {new == 7 * old})
    end
    return model, Dict("m" => m, "h" => h)
end
