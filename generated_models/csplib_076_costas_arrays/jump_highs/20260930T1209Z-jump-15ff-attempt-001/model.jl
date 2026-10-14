# Costas array: a permutation of 1..n in which, for every distance d up to n - 2,
# the differences costas[j] - costas[j - d] are all different.
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 1 <= costas[1:n] <= n, Int)
    @constraint(model, costas in MOI.AllDifferent(n))
    for d in 1:n-2
        diffs = @variable(model, [j = d+1:n], lower_bound = -(n - 1), upper_bound = n - 1, integer = true)
        @constraint(model, [j = d+1:n], diffs[j] == costas[j] - costas[j - d])
        @constraint(model, [diffs[j] for j in d+1:n] in MOI.AllDifferent(n - d))
    end
    return model, Dict("costas" => costas)
end
