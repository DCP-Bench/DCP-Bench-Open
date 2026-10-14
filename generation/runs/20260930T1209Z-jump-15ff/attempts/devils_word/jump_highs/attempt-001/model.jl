# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
using JuMP

function build(instance)
    arr = instance["arr"]
    total = instance["total"]
    n = length(arr)
    model = Model()
    @variable(model, plus[1:n], Bin)
    @variable(model, -abs(arr[i]) <= result[i = 1:n] <= abs(arr[i]), Int)
    # result[i] = arr[i] with its sign
    @constraint(model, [i = 1:n], result[i] == arr[i] * (2 * plus[i] - 1))
    @constraint(model, sum(result) == total)
    return model, Dict("result" => result)
end
