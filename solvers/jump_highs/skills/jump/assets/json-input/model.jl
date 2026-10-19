# Knapsack read from a JSON instance file: the instance path is the first argument, or instance.json next to this file.
using JuMP, HiGHS, JSON

inst = JSON.parsefile(get(ARGS, 1, joinpath(@__DIR__, "instance.json")))
weights = Int.(inst["weights"])
values = Int.(inst["values"])
capacity = Int(inst["capacity"])
n = length(weights)

model = Model(HiGHS.Optimizer)
set_silent(model)
set_attribute(model, "mip_rel_gap", 0.0)

@variable(model, take[1:n], Bin)
@constraint(model, sum(weights[i] * take[i] for i in 1:n) <= capacity)
@objective(model, Max, sum(values[i] * take[i] for i in 1:n))

optimize!(model)
if termination_status(model) != OPTIMAL || !has_values(model)
    println(stderr, "not proven optimal: ", termination_status(model))
    exit(1)
end
chosen = [round(Int, value(take[i])) for i in 1:n]
println("Status: ", termination_status(model))
println("Value: ", round(Int, objective_value(model)))
println("Take: [", join(chosen, ", "), "]")
