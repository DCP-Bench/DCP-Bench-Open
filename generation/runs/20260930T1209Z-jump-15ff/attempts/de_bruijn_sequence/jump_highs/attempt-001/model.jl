# De Bruijn sequence B(base, n): a cyclic sequence of base^n symbols from
# 0..base-1 in which every string of length n occurs exactly once. Row i of
# `binary` is the string starting at position i, and x[i] is its value.
using JuMP

function build(instance)
    base = instance["base"]
    n = instance["n"]
    m = base^n
    place = [base^(n - j) for j in 1:n]   # place value of each symbol
    model = Model()
    @variable(model, 0 <= binary[1:m, 1:n] <= base - 1, Int)
    @variable(model, 0 <= x[1:m] <= m - 1, Int)
    @constraint(model, [i = 1:m], x[i] == sum(place[j] * binary[i, j] for j in 1:n))
    # every string occurs once: the values of the m strings are all different
    @constraint(model, x in MOI.AllDifferent(m))
    # the string at position i + 1 is the string at i shifted by one symbol, and
    # the sequence wraps around
    @constraint(model, [i = 2:m, j = 2:n], binary[i - 1, j] == binary[i, j - 1])
    @constraint(model, [j = 2:n], binary[m, j] == binary[1, j - 1])
    return model, Dict("de_bruijn" => binary[:, 1])
end
