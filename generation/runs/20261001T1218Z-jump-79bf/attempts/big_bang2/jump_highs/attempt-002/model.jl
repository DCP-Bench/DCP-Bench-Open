# Big Bang nontransitive dice: five dice with six faces each, face values 1..12, such that the
# "beats" relation between the dice matches Rock-Paper-Scissors-Lizard-Spock. Die A beats die
# B when A shows a strictly larger face than B in more than half of all pairs of faces.
using JuMP

function build(instance)
    # The game is fixed by the problem; the instance carries no data.
    # Dice are numbered Rock = 1, Paper = 2, Scissors = 3, Lizard = 4, Spock = 5.
    m = 5    # number of dice
    n = 6    # number of faces of each die
    f = 12   # largest face value
    # the ten "winner beats loser" relationships of the game
    edge = [(1, 3), (1, 4),   # Rock crushes Scissors and Lizard
            (2, 1), (2, 5),   # Paper covers Rock and disproves Spock
            (3, 2), (3, 4),   # Scissors cuts Paper and decapitates Lizard
            (4, 2), (4, 5),   # Lizard eats Paper and poisons Spock
            (5, 1), (5, 3)]   # Spock vaporizes Rock and smashes Scissors

    model = Model()

    # Order encoding of the faces: reach[i, j, t] = 1 when face j of die i shows at least t
    # (t = 2..f; every face shows at least 1). The indicators can only switch off as t grows.
    @variable(model, reach[1:m, 1:n, 2:f], Bin)
    @constraint(model, [i = 1:m, j = 1:n, t = 2:f-1], reach[i, j, t+1] <= reach[i, j, t])

    # dice[i, j] = the value of face j of die i, the declared output, tied to the indicators
    @variable(model, 1 <= dice[1:m, 1:n] <= f, Int)
    @constraint(model, [i = 1:m, j = 1:n], dice[i, j] == 1 + sum(reach[i, j, t] for t in 2:f))

    # at_least(i, j, t) = 1 when face j of die i shows at least t: always for t <= 1, never for
    # t > f
    at_least(i, j, t) = t <= 1 ? 1 : (t > f ? 0 : reach[i, j, t])

    # For each relationship, the number of face pairs (x, y) with winner face x above loser
    # face y must exceed half of all n * n pairs. win[x, y] = 1 may only be set when
    # the winner face is above the loser face, which in the order encoding reads: for every
    # t, if the loser face reaches t then the winner face reaches t + 1. (This is stronger
    # for HiGHS than a big-M bound on the difference of the two face values.)
    for (winner, loser) in edge
        win = @variable(model, [1:n, 1:n], Bin)
        for x in 1:n, y in 1:n, t in 1:f
            @constraint(model, win[x, y] <= 1 - at_least(loser, y, t) + at_least(winner, x, t + 1))
        end
        @constraint(model, sum(win) >= div(n * n, 2) + 1)
    end

    return model, Dict("dice" => dice)
end
