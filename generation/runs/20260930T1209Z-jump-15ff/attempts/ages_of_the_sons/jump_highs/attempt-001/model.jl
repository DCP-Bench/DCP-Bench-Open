# Ages of the sons: three sons whose ages multiply to 36. Their sum does not tell
# them apart, so another triple with product 36 has the same sum; and there is
# an oldest son, so the oldest age is not shared.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    # the triples of ages 0..36, oldest first, whose product is 36
    triples = [(x, y, z) for x in 0:36 for y in 0:36 for z in 0:36 if x * y * z == 36]
    strict_triples = [t for t in triples if t[1] > t[2] >= t[3]]
    loose_triples = [t for t in triples if t[1] >= t[2] >= t[3]]
    strict = Float64[t[k] for t in strict_triples, k in 1:3]
    loose = Float64[t[k] for t in loose_triples, k in 1:3]
    model = Model()
    @variable(model, 0 <= age[1:3] <= 36, Int)
    @variable(model, 0 <= other[1:3] <= 36, Int)
    # the actual triple has a strictly oldest son; the other may have twins first
    @constraint(model, age in MOI.Table(strict))
    @constraint(model, other in MOI.Table(loose))
    # the same sum, and a different oldest age
    @constraint(model, sum(age) == sum(other))
    @constraint(model, [age[1], other[1]] in MOI.AllDifferent(2))
    return model, Dict("A1" => age[1], "A2" => age[2], "A3" => age[3])
end
