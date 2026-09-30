# Dinner: 1-6 grandparents at $3, 1-10 parents at $2 and 1-40 children at $0.50;
# twenty people in all, for $20.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, 1 <= grandparents <= 6, Int)
    @variable(model, 1 <= parents <= 10, Int)
    @variable(model, 1 <= children <= 40, Int)
    @constraint(model, 6 * grandparents + 4 * parents + children == 40)   # in half dollars
    @constraint(model, grandparents + parents + children == 20)
    return model, Dict("grandparents" => grandparents, "parents" => parents, "children" => children)
end
