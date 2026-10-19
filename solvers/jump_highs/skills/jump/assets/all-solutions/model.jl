# All solutions: list every integer pair (x, y) in 0..4 with x + 2y = 6.
using JuMP, HiGHS

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, 0 <= x <= 4, Int)
@variable(model, 0 <= y <= 4, Int)
@constraint(model, x + 2y == 6)

# Forbid one assignment: at least one variable must differ from its value a.
# A differing variable v has v >= a + 1 or v <= a - 1; binaries pick the side.
# Every variable must have finite bounds, which M is built from.
function exclude!(model, vars, values)
    t = @variable(model, [eachindex(vars)], Bin)
    for (k, v) in enumerate(vars)
        l, u = lower_bound(v), upper_bound(v)
        a = values[k]
        M = u - l + 1
        s = @variable(model, binary = true)
        @constraint(model, v >= a + 1 - M * (1 - s) - M * (1 - t[k]))
        @constraint(model, v <= a - 1 + M * s + M * (1 - t[k]))
    end
    @constraint(model, sum(t) >= 1)
end

# Each solve gives one solution; exclude it and solve again until none is left.
solutions = Tuple{Int, Int}[]
while true
    optimize!(model)
    termination_status(model) == OPTIMAL || break
    a = round.(Int, value.([x, y]))
    push!(solutions, (a[1], a[2]))
    exclude!(model, [x, y], a)
end

sort!(solutions)
println("Status after the last solve: ", termination_status(model))
println("Solutions: ", length(solutions))
for (xv, yv) in solutions
    println("x = $xv, y = $yv")
end
