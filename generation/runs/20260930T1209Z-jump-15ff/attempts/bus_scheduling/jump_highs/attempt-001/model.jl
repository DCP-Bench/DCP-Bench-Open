# Bus scheduling: the day is cut into time slots and a bus works two consecutive
# slots. Choose how many buses start in each slot so that every slot's demand is
# met with as few buses as possible.
using JuMP

function build(instance)
    demands = instance["demands"]
    n = length(demands)
    model = Model()
    # x[i] = the buses that start in slot i
    @variable(model, 0 <= x[1:n] <= sum(demands), Int)
    # slot i + 1 is served by the buses starting in slots i and i + 1 (the day wraps)
    @constraint(model, [i = 1:n], x[i] + x[mod1(i + 1, n)] >= demands[mod1(i + 1, n)])
    @objective(model, Min, sum(x))
    return model, Dict("x" => x)
end
