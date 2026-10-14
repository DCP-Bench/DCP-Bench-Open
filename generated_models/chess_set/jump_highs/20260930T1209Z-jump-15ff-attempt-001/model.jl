# Chess set: a joinery makes small and large boxwood chess sets. Decide how many
# of each to make in a week so that the boxwood and the lathe hours suffice and
# the profit is as large as possible.
using JuMP

function build(instance)
    # The problem statement fixes all the numbers; the instance carries no data.
    model = Model()
    @variable(model, 0 <= small_set <= 100, Int)
    @variable(model, 0 <= large_set <= 100, Int)
    @variable(model, 0 <= max_profit <= 10000, Int)
    # boxwood: 1 kg per small set, 3 kg per large set, 200 kg available
    @constraint(model, small_set + 3 * large_set <= 200)
    # lathe hours: 3 per small set, 2 per large set, 160 available
    @constraint(model, 3 * small_set + 2 * large_set <= 160)
    # profit: $5 per small set and $20 per large set
    @constraint(model, max_profit == 5 * small_set + 20 * large_set)
    @objective(model, Max, max_profit)
    return model, Dict("small_set" => small_set, "large_set" => large_set, "max_profit" => max_profit)
end
