# Three sum: choose m of the numbers so that they add up to zero.
using JuMP

function build(instance)
    nums = instance["nums"]
    m = instance["m"]
    n = length(nums)
    model = Model()
    @variable(model, indices[1:n], Bin)
    @constraint(model, sum(nums[i] * indices[i] for i in 1:n) == 0)
    @constraint(model, sum(indices) == m)
    return model, Dict("indices" => indices)
end
