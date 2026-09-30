# Climbing stairs: climb n steps taking between m1 and m2 steps at a time; each
# move is the steps taken, or 0 once the top is reached.
using JuMP

function build(instance)
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]
    model = Model()
    @variable(model, 0 <= steps[1:n] <= m2, Int)
    # moving[i] = 1 when move i takes steps, and then between m1 and m2 of them
    @variable(model, moving[1:n], Bin)
    @constraint(model, [i = 1:n], steps[i] >= m1 * moving[i])
    @constraint(model, [i = 1:n], steps[i] <= m2 * moving[i])
    # once a move is 0, every later move is 0 too
    @constraint(model, [i = 1:n-1], moving[i + 1] <= moving[i])
    @constraint(model, sum(steps) == n)
    return model, Dict("steps" => steps)
end
