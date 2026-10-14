# Ternary Steiner system of order n: n(n-1)/6 triples of the elements 1..n such
# that any two triples have at most one element in common.
using JuMP

function build(instance)
    n = instance["n"]
    nsets = div(n * (n - 1), 6)
    model = Model()
    # sets[i, j] = 1 when element j belongs to triple i
    @variable(model, sets[1:nsets, 1:n], Bin)
    @constraint(model, [i = 1:nsets], sum(sets[i, :]) == 3)
    # two triples share at most one element: both[j] is at least 1 when element j
    # is in both, and at most one element may be
    for i1 in 1:nsets-1, i2 in i1+1:nsets
        both = @variable(model, [1:n], Bin)
        @constraint(model, [j = 1:n], both[j] >= sets[i1, j] + sets[i2, j] - 1)
        @constraint(model, sum(both) <= 1)
    end
    return model, Dict("sets" => sets)
end
