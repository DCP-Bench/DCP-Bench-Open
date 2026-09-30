# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across a
# river in a boat that carries him and at most one item. The wolf is never left
# alone with the goat, nor the goat with the cabbage. For each stage the answer
# gives the shore (0 = start, 1 = far side) of each item and of the boat.
using JuMP

function build(instance)
    stage = instance["stage"]
    model = Model()
    @variable(model, wolf[1:stage], Bin)
    @variable(model, goat[1:stage], Bin)
    @variable(model, cabbage[1:stage], Bin)
    @variable(model, boat[1:stage], Bin)
    # everything starts on the first shore and ends on the far one
    for x in (wolf, goat, cabbage, boat)
        fix(x[1], 0; force = true)
        fix(x[stage], 1; force = true)
    end
    # the boat crosses at every stage
    @constraint(model, [i = 2:stage], boat[i] + boat[i - 1] == 1)
    for i in 1:stage, (a, b) in ((wolf, goat), (goat, cabbage))
        # two that share a shore have the boat there: not both on 1 with the boat on 0,
        # and not both on 0 with the boat on 1
        @constraint(model, a[i] + b[i] - boat[i] <= 1)
        @constraint(model, boat[i] - a[i] - b[i] <= 0)
    end
    # at most one item changes shore between two stages
    @variable(model, moved[1:stage-1, 1:3], Bin)
    for i in 1:stage-1, (k, x) in enumerate((wolf, goat, cabbage))
        @constraint(model, moved[i, k] >= x[i + 1] - x[i])
        @constraint(model, moved[i, k] >= x[i] - x[i + 1])
    end
    @constraint(model, [i = 1:stage-1], sum(moved[i, :]) <= 1)
    return model, Dict("wolf_pos" => wolf, "goat_pos" => goat, "cabbage_pos" => cabbage, "boat_pos" => boat)
end
