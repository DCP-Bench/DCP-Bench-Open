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

    # dice[i, j] = the value of face j of die i
    @variable(model, 1 <= dice[1:m, 1:n] <= f, Int)

    # For each relationship, the number of face pairs (x, y) with winner face x above loser
    # face y must exceed half of all n * n pairs. win[x, y] = 1 may only be set when that
    # pair really has dice[winner, x] - dice[loser, y] >= 1; the difference is at least
    # 1 - f, so the big-M is f (the constraint is slack when win is 0).
    for (winner, loser) in edge
        win = @variable(model, [1:n, 1:n], Bin)
        @constraint(model, [x = 1:n, y = 1:n],
                    dice[winner, x] - dice[loser, y] >= 1 - f * (1 - win[x, y]))
        @constraint(model, sum(win) >= div(n * n, 2) + 1)
    end

    return model, Dict("dice" => dice)
end
