# Four numbers: given up to four distinct integers between 1 and 10, find three
# integers between 1 and 10 such that every given number is the sum of some
# subset of the three.
using JuMP

function build(instance)
    numbers = instance["numbers"]
    m = length(numbers)
    model = Model()
    @variable(model, 1 <= x[1:3] <= 10, Int)
    # use[i, j] = 1 when x[j] belongs to the subset that makes numbers[i], and
    # part[i, j] = use[i, j] * x[j], linearised with x at most 10
    @variable(model, use[1:m, 1:3], Bin)
    @variable(model, 0 <= part[1:m, 1:3] <= 10, Int)
    @constraint(model, [i = 1:m, j = 1:3], part[i, j] <= 10 * use[i, j])
    @constraint(model, [i = 1:m, j = 1:3], part[i, j] <= x[j])
    @constraint(model, [i = 1:m, j = 1:3], part[i, j] >= x[j] - 10 * (1 - use[i, j]))
    @constraint(model, [i = 1:m], sum(part[i, :]) == numbers[i])
    return model, Dict("x" => x)
end
