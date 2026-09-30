# A curious set of integers: 1, 3, 8 and 120 have the property that the product
# of any two is one less than a square. Find a fifth number (0 or more) that
# keeps the property.
using JuMP

function build(instance)
    n = instance["n"]
    maxval = instance["max_val"]
    known = [1, 3, 8, 120]
    model = Model()
    @variable(model, 0 <= number <= maxval, Int)
    @constraint(model, [number; known] in MOI.AllDifferent(n))
    # the products among the given numbers are already one less than a square
    # (4, 9, 121, 25, 361, 961), so only the products with the new number matter:
    # c * number + 1 is the square of a root at most sqrt(c * maxval + 1)
    for c in known
        top = isqrt(c * maxval + 1)
        root = @variable(model, [0:top], Bin)
        @constraint(model, sum(root) == 1)
        @constraint(model, c * number + 1 == sum(r^2 * root[r] for r in 0:top))
    end
    return model, Dict("number" => number)
end
