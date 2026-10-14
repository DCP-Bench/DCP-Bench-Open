# Guards and apples: a boy passes several gates. At each gate he gives the guard
# half of his apples plus one, and after the last gate one apple is left.
using JuMP

function build(instance)
    gates = instance["num_gates"]
    model = Model()
    # apples[i] = the apples before gate i; the last entry is what is left
    @variable(model, 0 <= apples[1:gates+1] <= 100, Int)
    @constraint(model, apples[gates + 1] == 1)
    # the guard gets half plus one, so before = 2 * (after + 1)
    @constraint(model, [i = 1:gates], apples[i] == 2 * (apples[i + 1] + 1))
    return model, Dict("apples" => apples)
end
