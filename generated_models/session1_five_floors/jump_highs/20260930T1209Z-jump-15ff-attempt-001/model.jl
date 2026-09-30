# Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
# of a five-floor house; the clues rule out some floors and some neighbours.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    names = ["B", "C", "F", "M", "S"]   # Baker, Cooper, Fletcher, Miller, Smith
    model = Model()
    # on[p, v] = 1 when person p lives on floor v
    @variable(model, on[1:5, 1:5], Bin)
    @constraint(model, [p = 1:5], sum(on[p, :]) == 1)
    @constraint(model, [v = 1:5], sum(on[:, v]) == 1)
    @variable(model, 1 <= floor[1:5] <= 5, Int)
    @constraint(model, [p = 1:5], floor[p] == sum(v * on[p, v] for v in 1:5))
    b, c, f, m, s = 1:5
    fix(on[b, 5], 0; force = true)      # Baker not on the fifth floor
    fix(on[c, 1], 0; force = true)      # Cooper not on the first
    fix(on[f, 5], 0; force = true)      # Fletcher neither on the fifth ...
    fix(on[f, 1], 0; force = true)      # ... nor on the first
    @constraint(model, floor[m] >= floor[c] + 1)   # Miller above Cooper
    # Smith not next to Fletcher, and Fletcher not next to Cooper
    for (p, q) in ((s, f), (f, c)), v in 1:4
        @constraint(model, on[p, v] + on[q, v + 1] <= 1)
        @constraint(model, on[q, v] + on[p, v + 1] <= 1)
    end
    return model, Dict(names[p] => floor[p] for p in 1:5)
end
