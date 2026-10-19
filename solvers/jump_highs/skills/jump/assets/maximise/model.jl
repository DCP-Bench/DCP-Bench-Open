# Maximise: integer production plan for two products under two resource limits.
using JuMP, HiGHS

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, a >= 0, Int)        # units of product A
@variable(model, b >= 0, Int)        # units of product B
@constraint(model, 6a + 4b <= 24)    # material
@constraint(model, a + 2b <= 6)      # labour
@objective(model, Max, 5a + 4b)

optimize!(model)
println("Status: ", termination_status(model))
println("A = ", round(Int, value(a)), ", B = ", round(Int, value(b)))
println("Profit: ", round(Int, objective_value(model)))
