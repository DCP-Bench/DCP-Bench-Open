# Infeasible: two integers in 0..2 that must sum to at least 5.
using JuMP, HiGHS

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, 0 <= x <= 2, Int)
@variable(model, 0 <= y <= 2, Int)
@constraint(model, x + y >= 5)

optimize!(model)
println("Status: ", termination_status(model))
println("Has a solution: ", has_values(model))
