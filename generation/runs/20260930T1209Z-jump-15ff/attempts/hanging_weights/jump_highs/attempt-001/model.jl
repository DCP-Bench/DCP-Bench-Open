# Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
# different, hang from a system of bars that has to balance.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    model = Model()
    @variable(model, 1 <= w[1:13] <= 13, Int)
    a, b, c, d, e, f, g, h, i, j, k, l, m = w
    @constraint(model, w in MOI.AllDifferent(13))
    # every bar balances: weights times their distance from the pivot, a bar
    # hanging beneath another counting as one weight equal to its total
    @constraint(model, 4 * a == b)
    @constraint(model, 5 * c == d)
    @constraint(model, 3 * e == 2 * f)
    @constraint(model, 3 * g == 2 * (c + d))
    @constraint(model, 3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    @constraint(model, 3 * h == 2 * (e + f) + 3 * i)
    @constraint(model, h + i + e + f == l + 4 * m)
    @constraint(model, 4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))
    return model, Dict(string(name) => w[n] for (n, name) in enumerate("abcdefghijklm"))
end
