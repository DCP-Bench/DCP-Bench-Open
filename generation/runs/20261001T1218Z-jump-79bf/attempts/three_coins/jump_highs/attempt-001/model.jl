# Three coins: the coins lie in the order given by `init` (1 = tails, 0 = heads). In exactly
# `num_moves` moves, each flipping one coin, make them all heads or all tails.
using JuMP

function build(instance)
    num_moves = instance["num_moves"]
    init = instance["init"]
    n = length(init)   # number of coins

    model = Model()

    # steps[m + 1, j] = the face of coin j after m moves (1 = tails, 0 = heads); row 1 is the
    # starting position
    @variable(model, steps[1:num_moves+1, 1:n], Bin)
    @constraint(model, [j = 1:n], steps[1, j] == init[j])

    # Exactly one coin differs between consecutive positions. flipped[m, j] = 1 exactly when
    # coin j differs between position m and m + 1, i.e. the exclusive or of the two faces.
    @variable(model, flipped[1:num_moves, 1:n], Bin)
    for m in 1:num_moves, j in 1:n
        before, after = steps[m, j], steps[m+1, j]
        @constraint(model, flipped[m, j] >= after - before)
        @constraint(model, flipped[m, j] >= before - after)
        @constraint(model, flipped[m, j] <= before + after)
        @constraint(model, flipped[m, j] <= 2 - before - after)
    end
    @constraint(model, [m = 1:num_moves], sum(flipped[m, :]) == 1)

    # The last position is all heads or all tails: the number of tails is 0 or n.
    all_tails = @variable(model, binary = true)
    @constraint(model, sum(steps[num_moves+1, :]) == n * all_tails)

    return model, Dict("steps" => steps)
end
