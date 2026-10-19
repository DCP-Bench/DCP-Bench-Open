# Satisfy: find one permutation of 1..4 that meets two linear side conditions.
using JuMP, HiGHS

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, 1 <= x[1:4] <= 4, Int)
@constraint(model, x in MOI.AllDifferent(4))   # the four values are distinct
@constraint(model, x[1] + 1 <= x[2])           # x[1] < x[2] for integers
@constraint(model, x[3] + x[4] == 5)

# No objective: the solver stops at the first feasible point.
optimize!(model)
println("Status: ", termination_status(model))
if has_values(model)
    sol = round.(Int, value.(x))
    println("x = ", sol)
    println("Valid: ", sol[1] < sol[2] && sol[3] + sol[4] == 5 && allunique(sol))
end
