# Magic sequence: a sequence x[0..n-1] of integers between 0 and n-1 such that,
# for every i, the number i occurs exactly x[i] times in the sequence.
using JuMP

function build(instance)
    n = instance["n"]   # length of the sequence; the values lie in 0..n-1
    model = Model()

    # is_val[i, v] = 1 when position i holds the value v (v is 0-based, stored at v + 1)
    @variable(model, is_val[1:n, 1:n], Bin)
    # each position holds exactly one value
    @constraint(model, [i = 1:n], sum(is_val[i, :]) == 1)

    # x[i] is the value held at position i, a declared output
    @variable(model, 0 <= x[1:n] <= n - 1, Int)
    @constraint(model, [i = 1:n], x[i] == sum((v - 1) * is_val[i, v] for v in 1:n))

    # the number i occurs exactly x[i] times: count the positions holding i
    @constraint(model, [i = 1:n], x[i] == sum(is_val[:, i]))

    return model, Dict("x" => x)
end
