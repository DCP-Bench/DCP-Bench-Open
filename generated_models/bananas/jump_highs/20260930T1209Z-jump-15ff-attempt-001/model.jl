# Bananas: five bananas cost $3, seven oranges $5, nine mangoes $7 and three
# apples $9. Buy 100 fruits for $100, some of every kind, with as few bananas and
# apples as possible.
using JuMP

function build(instance)
    # The puzzle has no data.
    model = Model()
    @variable(model, 1 <= x[1:4] <= 100, Int)
    bananas, oranges, mangoes, apples = x
    # the cost, times 3 * 5 * 7 * 9 = 945 to clear the fractions
    @constraint(model, 3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes + 9 * 315 * apples == 100 * 945)
    @constraint(model, sum(x) == 100)
    @objective(model, Min, bananas + apples)
    return model, Dict("bananas" => bananas, "oranges" => oranges, "mangoes" => mangoes, "apples" => apples)
end
