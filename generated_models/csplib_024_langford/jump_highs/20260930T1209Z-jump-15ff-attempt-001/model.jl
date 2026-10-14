# Langford's problem L(2, k): arrange two copies of each of 1..k in a sequence of
# 2k numbers so that the two copies of i are i numbers apart (their positions
# differ by i + 1).
using JuMP

function build(instance)
    k = instance["k"]
    len = 2k
    model = Model()
    # first[i, p] = 1 when the first copy of i is at position p; the second is then at p + i + 1
    @variable(model, first[i = 1:k, p = 1:len-i-1], Bin)
    @constraint(model, [i = 1:k], sum(first[i, p] for p in 1:len-i-1) == 1)
    # the copy of i at position p, if any
    copy_at(i, p) = (p <= len - i - 1 ? first[i, p] : 0) + (p - i - 1 >= 1 ? first[i, p - i - 1] : 0)
    # every position holds exactly one number
    @constraint(model, [p = 1:len], sum(copy_at(i, p) for i in 1:k) == 1)
    @variable(model, 1 <= sol[1:len] <= k, Int)
    @constraint(model, [p = 1:len], sol[p] == sum(i * copy_at(i, p) for i in 1:k))
    return model, Dict("sol" => sol)
end
