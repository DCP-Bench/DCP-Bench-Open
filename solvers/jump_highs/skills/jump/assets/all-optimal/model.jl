# All optimal solutions: choose items to maximise value within capacity 4,
# then list every selection that reaches the optimum.
using JuMP, HiGHS

value_of = [5, 5, 5, 1]
weight_of = [2, 2, 2, 3]
capacity = 4

model = Model(HiGHS.Optimizer)
set_silent(model)

@variable(model, x[eachindex(value_of)], Bin)
@constraint(model, sum(weight_of[i] * x[i] for i in eachindex(x)) <= capacity)
@objective(model, Max, sum(value_of[i] * x[i] for i in eachindex(x)))
optimize!(model)
best = round(Int, objective_value(model))
println("Optimal value: ", best)

# Pin the objective to the optimum and turn the model into a pure feasibility problem.
@constraint(model, sum(value_of[i] * x[i] for i in eachindex(x)) == best)
set_objective_sense(model, MOI.FEASIBILITY_SENSE)

# Forbid one selection: at least one item must flip (1 -> 0 or 0 -> 1).
function exclude!(model, vars, values)
    @constraint(model, sum(values[k] == 1 ? 1 - v : v for (k, v) in enumerate(vars)) >= 1)
end

selections = Vector{Int}[]
while true
    optimize!(model)
    termination_status(model) == OPTIMAL || break
    s = round.(Int, value.(x))
    push!(selections, s)
    exclude!(model, x, s)
end

println("Optimal selections: ", length(selections))
for s in sort(selections)
    println("items ", findall(==(1), s))
end
