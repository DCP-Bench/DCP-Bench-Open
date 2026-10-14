# Best host: seat six guests round a table so that everyone sits only next to
# guests they are willing to sit next to.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    # prefs[g] = the guests (0-based) that guest g - 1 will sit next to
    prefs = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]
    n = 6
    model = Model()
    # at[i, g] = 1 when seat i holds guest g - 1
    @variable(model, at[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(at[i, :]) == 1)
    @constraint(model, [g = 1:n], sum(at[:, g]) == 1)
    # two guests who are not both willing never sit side by side
    for i in 1:n, g in 1:n, h in 1:n
        willing = (h - 1) in prefs[g] && (g - 1) in prefs[h]
        willing || @constraint(model, at[i, g] + at[mod1(i + 1, n), h] <= 1)
    end
    @variable(model, 0 <= x[1:n] <= n - 1, Int)
    @constraint(model, [i = 1:n], x[i] == sum((g - 1) * at[i, g] for g in 1:n))
    return model, Dict("x" => x)
end
