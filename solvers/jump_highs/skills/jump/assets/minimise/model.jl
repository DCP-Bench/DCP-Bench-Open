# Minimise: cheapest collection of sets that covers every element (set cover).
using JuMP, HiGHS

n_elements = 5
sets = [[1, 2, 3], [2, 4], [3, 4, 5], [1, 5], [4]]
cost = [3, 2, 3, 2, 1]

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, pick[eachindex(sets)], Bin)
for e in 1:n_elements
    @constraint(model, sum(pick[s] for s in eachindex(sets) if e in sets[s]) >= 1)
end
@objective(model, Min, sum(cost[s] * pick[s] for s in eachindex(sets)))

optimize!(model)
println("Status: ", termination_status(model))
println("Minimum cost: ", round(Int, objective_value(model)))
println("Chosen sets: ", [s for s in eachindex(sets) if value(pick[s]) > 0.5])
