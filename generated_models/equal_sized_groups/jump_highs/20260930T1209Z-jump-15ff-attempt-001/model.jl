# Equal-sized groups: split a sorted list into k groups at k - 1 break points,
# never separating equal values, so that the group sizes are as close as
# possible to round(n / k).
using JuMP

function build(instance)
    a = instance["a"]
    k = instance["k"]
    n = length(a)
    # the ideal size, round(n / k) with halves to the even number, as Python rounds
    gsize = Int(round(n / k, RoundNearest))
    # a break after element j is allowed when a[j] != a[j + 1]
    allowed = [j for j in 1:n-1 if a[j] != a[j + 1]]
    model = Model()
    # at[p, j] = 1 when break point p is after element allowed[j]
    @variable(model, at[1:k-1, 1:length(allowed)], Bin)
    @constraint(model, [p = 1:k-1], sum(at[p, :]) == 1)
    @variable(model, 1 <= x[1:k-1] <= n, Int)
    @constraint(model, [p = 1:k-1], x[p] == sum(allowed[j] * at[p, j] for j in 1:length(allowed)))
    # group sizes, each at least 1, which also orders the break points
    @variable(model, 1 <= s[1:k] <= n, Int)
    @constraint(model, s[1] == x[1])
    @constraint(model, [i = 2:k-1], s[i] == x[i] - x[i - 1])
    @constraint(model, s[k] == n - x[k - 1])
    # the distance of each size from the ideal, exact because it is minimised
    @variable(model, 0 <= dev[1:k] <= n, Int)
    @constraint(model, [i = 1:k], dev[i] >= s[i] - gsize)
    @constraint(model, [i = 1:k], dev[i] >= gsize - s[i])
    @objective(model, Min, sum(dev))
    return model, Dict("x" => x)
end
