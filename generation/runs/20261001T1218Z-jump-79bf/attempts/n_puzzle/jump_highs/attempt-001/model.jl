# N-puzzle: a square board holds the numbered tiles 1..n and one empty square (0). Slide
# tiles into the empty square, one tile per step, to get from the start arrangement to the
# end arrangement in exactly N_STEPS states (start and end included).
using JuMP

function build(instance)
    T = instance["N_STEPS"]           # number of states, start and end included
    start = instance["puzzle_start"]
    goal = instance["puzzle_end"]
    dim = length(start)               # the board is dim x dim
    values = 0:dim*dim-1              # 0 is the empty square

    model = Model()

    # at[t, i, j, v] = 1 when, in state t, square (i, j) holds v (0 = empty). In every state
    # each square holds one value and each value is on one square (all squares different).
    @variable(model, at[t = 1:T, i = 1:dim, j = 1:dim, v = values], Bin)
    @constraint(model, [t = 1:T, i = 1:dim, j = 1:dim], sum(at[t, i, j, v] for v in values) == 1)
    @constraint(model, [t = 1:T, v = values], sum(at[t, i, j, v] for i in 1:dim, j in 1:dim) == 1)

    # The first state is the start arrangement and the last state is the end arrangement
    for i in 1:dim, j in 1:dim
        @constraint(model, at[1, i, j, start[i][j]] == 1)
        @constraint(model, at[T, i, j, goal[i][j]] == 1)
    end

    # touching(i, j) = the squares that share a side with square (i, j)
    touching(i, j) = [(i + a, j + b) for (a, b) in ((-1, 0), (1, 0), (0, -1), (0, 1))
                      if 1 <= i + a <= dim && 1 <= j + b <= dim]
    for t in 2:T, i in 1:dim, j in 1:dim
        # The empty square must move at every step (the state may not stay the same), and
        # it moves to a square that touches its old one.
        @constraint(model, at[t, i, j, 0] <= sum(at[t-1, p, q, 0] for (p, q) in touching(i, j)))
        @constraint(model, at[t, i, j, 0] + at[t-1, i, j, 0] <= 1)
        # Only the empty square moves: a square that is empty neither before nor after keeps
        # its tile. A tile v on (i, j) before stays there unless that square becomes empty,
        # and a tile on (i, j) after was there before unless that square was empty.
        for v in 1:dim*dim-1
            @constraint(model, at[t-1, i, j, v] <= at[t, i, j, v] + at[t, i, j, 0])
            @constraint(model, at[t, i, j, v] <= at[t-1, i, j, v] + at[t-1, i, j, 0])
        end
    end

    # steps[t][i, j] = the tile on square (i, j) in state t (declared output)
    steps = [[sum(v * at[t, i, j, v] for v in values) for i in 1:dim, j in 1:dim] for t in 1:T]
    return model, Dict("steps" => steps)
end
