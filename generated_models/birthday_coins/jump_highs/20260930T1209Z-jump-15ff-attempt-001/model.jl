# Birthday coins: 15 coins (half-crowns, shillings and sixpences) worth 1 pound
# 5 shillings 6 pence. How many half-crowns?
using JuMP

function build(instance)
    # The puzzle is fixed by the problem; the instance carries no data.
    values = [30, 12, 6]      # pence in a half-crown, a shilling, a sixpence
    model = Model()
    @variable(model, 0 <= coins[1:3] <= 15, Int)
    @constraint(model, sum(values[t] * coins[t] for t in 1:3) == 240 + 5 * 12 + 6)
    @constraint(model, sum(coins) == 15)
    return model, Dict("half_crowns" => coins[1])
end
