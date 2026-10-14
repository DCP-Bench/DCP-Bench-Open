# Fifty puzzle: knock over dummies whose numbers add up to exactly the target.
using JuMP

function build(instance)
    target = instance["target_sum"]
    values = instance["values"]
    n = length(values)
    model = Model()
    @variable(model, dummies[1:n], Bin)
    @constraint(model, sum(values[i] * dummies[i] for i in 1:n) == target)
    return model, Dict("dummies" => dummies)
end
