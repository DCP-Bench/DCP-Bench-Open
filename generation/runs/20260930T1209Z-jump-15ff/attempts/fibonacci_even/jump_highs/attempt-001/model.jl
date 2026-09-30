# Fibonacci even: add up the even-valued terms of the Fibonacci sequence that do
# not exceed four million.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 35             # terms f_1 .. f_35 are considered; the largest is below 10 million
    big = 10_000_000
    model = Model()
    # f[i + 1] = the i-th Fibonacci number: f_0 = 0, f_1 = f_2 = 1, then the sum of the previous two
    @variable(model, 0 <= f[1:n+1] <= big, Int)
    fix(f[1], 0; force = true); fix(f[2], 1; force = true); fix(f[3], 1; force = true)
    @constraint(model, [i = 4:n+1], f[i] == f[i - 1] + f[i - 2])
    # f = 2 * half + odd; below = 1 exactly when f < 4000000; taken = below and not odd
    @variable(model, 0 <= half[1:n+1] <= div(big, 2), Int)
    @variable(model, odd[1:n+1], Bin)
    @variable(model, below[1:n+1], Bin)
    @variable(model, taken[1:n+1], Bin)
    @constraint(model, [i = 1:n+1], f[i] == 2 * half[i] + odd[i])
    @constraint(model, [i = 1:n+1], below[i] --> {f[i] <= 3_999_999})
    @constraint(model, [i = 1:n+1], !below[i] --> {f[i] >= 4_000_000})
    @constraint(model, [i = 1:n+1], taken[i] <= below[i])
    @constraint(model, [i = 1:n+1], taken[i] <= 1 - odd[i])
    @constraint(model, [i = 1:n+1], taken[i] >= below[i] - odd[i])
    # part = taken * f, linearised with f at most big
    @variable(model, 0 <= part[1:n+1] <= big, Int)
    @constraint(model, [i = 1:n+1], part[i] <= big * taken[i])
    @constraint(model, [i = 1:n+1], part[i] <= f[i])
    @constraint(model, [i = 1:n+1], part[i] >= f[i] - big * (1 - taken[i]))
    @variable(model, 0 <= res <= 100_000_000, Int)
    @constraint(model, res == sum(part[i] for i in 2:n+1))
    return model, Dict("res" => res)
end
