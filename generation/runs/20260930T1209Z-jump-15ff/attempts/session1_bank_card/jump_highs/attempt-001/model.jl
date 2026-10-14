# Bank card: a PIN abcd with four different digits, where cd = 3 * ab and
# da = 2 * bc, each read as a two-digit number.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, 0 <= pin[1:4] <= 9, Int)
    a, b, c, d = pin
    @constraint(model, pin in MOI.AllDifferent(4))
    @constraint(model, 10 * c + d == 3 * (10 * a + b))
    @constraint(model, 10 * d + a == 2 * (10 * b + c))
    return model, Dict("a" => a, "b" => b, "c" => c, "d" => d)
end
