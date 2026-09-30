# Bowls and oranges: put oranges in bowls placed in a line, at most one per bowl,
# so that no three oranges are at equal distances (B - A = C - B).
using JuMP

function build(instance)
    bowls = instance["n"]
    oranges = instance["m"]
    model = Model()
    # at[i, p] = 1 when the i-th orange (in ascending order) is in bowl p
    @variable(model, at[1:oranges, 1:bowls], Bin)
    @constraint(model, [i = 1:oranges], sum(at[i, :]) == 1)
    @variable(model, 1 <= x[1:oranges] <= bowls, Int)
    @constraint(model, [i = 1:oranges], x[i] == sum(p * at[i, p] for p in 1:bowls))
    # ascending bowls, so at most one orange per bowl
    @constraint(model, [i = 1:oranges-1], x[i] + 1 <= x[i + 1])
    # no three occupied bowls p, p + d, p + 2 * d
    occupied = [sum(at[i, p] for i in 1:oranges) for p in 1:bowls]
    for p in 1:bowls, d in 1:div(bowls - p, 2)
        @constraint(model, occupied[p] + occupied[p + d] + occupied[p + 2 * d] <= 2)
    end
    return model, Dict("x" => x)
end
