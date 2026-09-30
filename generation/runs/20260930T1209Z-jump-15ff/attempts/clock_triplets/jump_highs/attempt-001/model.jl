# Clock triplets: arrange the numbers 1 to 12 on a clock face so that no three
# neighbouring numbers add up to more than 21.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    n = 12
    model = Model()
    @variable(model, 1 <= x[1:n] <= n, Int)
    @constraint(model, x in MOI.AllDifferent(n))
    @constraint(model, [i = 1:n], x[i] + x[mod1(i + 1, n)] + x[mod1(i + 2, n)] <= 21)
    return model, Dict("x" => x)
end
