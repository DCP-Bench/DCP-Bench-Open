# Bin packing: assign each item to one of num_bins bins so that the total weight
# of the items in a bin does not exceed the bin capacity.
using JuMP

function build(instance)
    weights = instance["weights"]     # weight of each item
    capacity = instance["capacity"]   # capacity of every bin
    num_bins = instance["num_bins"]
    n = length(weights)

    model = Model()

    # in_bin[i, b] = 1 when item i is put in bin b
    @variable(model, in_bin[1:n, 1:num_bins], Bin)
    # each item goes in exactly one bin
    @constraint(model, [i = 1:n], sum(in_bin[i, :]) == 1)

    # bins[i] = the (0-based) bin of item i, a declared output
    @variable(model, 0 <= bins[1:n] <= num_bins - 1, Int)
    @constraint(model, [i = 1:n], bins[i] == sum((b - 1) * in_bin[i, b] for b in 1:num_bins))

    # the weight in each bin stays within the capacity
    @constraint(model, [b = 1:num_bins], sum(weights[i] * in_bin[i, b] for i in 1:n) <= capacity)

    return model, Dict("bins" => bins)
end
