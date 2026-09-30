# Huey, Dewey and Louie cannot lie. Huey: Dewey and Louie share the guilt
# equally. Dewey: if Huey is guilty, so am I. Louie: Dewey and I are not both guilty.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, huey, Bin); @variable(model, dewey, Bin); @variable(model, louie, Bin)
    @constraint(model, dewey == louie)
    @constraint(model, huey <= dewey)
    @constraint(model, dewey + louie <= 1)
    return model, Dict("huey" => huey, "dewey" => dewey, "louie" => louie)
end
