# Two subsets with equal sums: find disjoint non-empty subsets S and T of A with
# the same sum.
using JuMP

function build(instance)
    A = instance["A"]
    n = length(A)
    model = Model()
    @variable(model, in_S[1:n], Bin)
    @variable(model, in_T[1:n], Bin)
    # the sums are equal
    @constraint(model, sum(A[i] * in_S[i] for i in 1:n) == sum(A[i] * in_T[i] for i in 1:n))
    # S and T are disjoint and not empty
    @constraint(model, [i = 1:n], in_S[i] + in_T[i] <= 1)
    @constraint(model, sum(in_S) >= 1)
    @constraint(model, sum(in_T) >= 1)
    return model, Dict("in_S" => in_S, "in_T" => in_T)
end
