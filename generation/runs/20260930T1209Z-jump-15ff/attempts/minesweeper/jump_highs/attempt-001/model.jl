# Minesweeper: decide which unopened cells hold mines. An opened cell holds no
# mine, and its number counts the mines among its (up to eight) neighbours.
using JuMP

function build(instance)
    unopened = instance["X"]    # the value marking an unopened cell
    game = instance["game_data"]
    r, c = length(game), length(game[1])
    model = Model()
    @variable(model, mines[1:r, 1:c], Bin)
    for i in 1:r, j in 1:c
        value = game[i][j]
        value == unopened && continue
        # an opened cell holds no mine, and its number counts the mines around it
        fix(mines[i, j], 0; force = true)
        @constraint(model, sum(mines[i + a, j + b] for a in -1:1, b in -1:1
                               if (a, b) != (0, 0) && 1 <= i + a <= r && 1 <= j + b <= c) == value)
    end
    return model, Dict("mines" => mines)
end
