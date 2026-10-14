# Farmer and cows: cow i gives i units of milk. Share the cows among the sons so
# that every son gets his number of cows and all sons get the same milk.
using JuMP

function build(instance)
    cows = instance["num_cows"]
    sons = instance["num_sons"]
    per_son = instance["cows_per_son"]
    milk = div(div(cows * (cows + 1), 2), sons)
    model = Model()
    # gets[i, s] = 1 when cow i goes to son s - 1
    @variable(model, gets[1:cows, 1:sons], Bin)
    @constraint(model, [i = 1:cows], sum(gets[i, :]) == 1)
    @constraint(model, [s = 1:sons], sum(gets[:, s]) == per_son[s])
    @constraint(model, [s = 1:sons], sum(i * gets[i, s] for i in 1:cows) == milk)
    @variable(model, 0 <= assignment[1:cows] <= sons - 1, Int)
    @constraint(model, [i = 1:cows], assignment[i] == sum((s - 1) * gets[i, s] for s in 1:sons))
    return model, Dict("cow_assignments" => assignment)
end
