# All-interval series: order the pitch classes 0..n-1 so that the absolute
# differences between neighbours are also all different (they are 1..n-1).
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x[1:n] <= n - 1, Int)
    @variable(model, 1 <= diffs[1:n-1] <= n - 1, Int)
    @constraint(model, x in MOI.AllDifferent(n))
    @constraint(model, diffs in MOI.AllDifferent(n - 1))
    # diffs[i] = |x[i + 1] - x[i]|, exactly, with a binary choosing the sign
    @variable(model, side[1:n-1], Bin)
    for i in 1:n-1
        @constraint(model, diffs[i] >= x[i + 1] - x[i])
        @constraint(model, diffs[i] >= x[i] - x[i + 1])
        @constraint(model, diffs[i] <= x[i + 1] - x[i] + 2 * (n - 1) * side[i])
        @constraint(model, diffs[i] <= x[i] - x[i + 1] + 2 * (n - 1) * (1 - side[i]))
    end
    return model, Dict("x" => x, "diffs" => diffs)
end
