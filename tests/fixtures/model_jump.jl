using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    if instance["optimize"]
        @constraint(model, x + y >= n)
        @objective(model, Min, x + y)
    else
        @constraint(model, x + y == n)
    end
    return model, Dict("x" => x, "y" => y)
end
