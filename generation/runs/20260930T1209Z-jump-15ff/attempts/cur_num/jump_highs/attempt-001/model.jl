# Curious number: adding 1 to 48 gives a square, and adding 1 to its half does
# too. Find another number from 1 to 10000 with the same peculiarity.
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    roots = 1:100      # square roots of squares up to 10000
    model = Model()
    @variable(model, 1 <= peculiar <= 9999, Int)
    @variable(model, 1 <= half <= 5000, Int)
    # which root each square has
    @variable(model, r1[roots], Bin)
    @variable(model, r2[roots], Bin)
    @constraint(model, sum(r1) == 1)
    @constraint(model, sum(r2) == 1)
    # peculiar + 1 is a square, peculiar is twice half, and half + 1 is a square
    @constraint(model, peculiar + 1 == sum(k^2 * r1[k] for k in roots))
    @constraint(model, peculiar == 2 * half)
    @constraint(model, half + 1 == sum(k^2 * r2[k] for k in roots))
    # 48 is already known; peculiar is 7 * 7 - 1 exactly when r1[7] is set
    fix(r1[7], 0; force = true)
    return model, Dict("peculiar" => peculiar)
end
