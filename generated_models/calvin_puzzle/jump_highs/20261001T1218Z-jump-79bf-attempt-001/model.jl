# Calvin puzzle: fill an n by n grid with the numbers 1..n*n, each once, so that every
# number k+1 sits three squares from k horizontally or vertically (two squares between
# them), or two squares diagonally (one square between them).
using JuMP

function build(instance)
    n = instance["n"]   # grid side
    cells = n * n       # squares, and also the largest number to place

    model = Model()

    # at[k, i, j] = 1 when the number k is written in square (i, j)
    @variable(model, at[1:cells, 1:n, 1:n], Bin)

    # each number goes in exactly one square
    @constraint(model, [k = 1:cells], sum(at[k, :, :]) == 1)
    # each square holds exactly one number (the numbers are all different)
    @constraint(model, [i = 1:n, j = 1:n], sum(at[:, i, j]) == 1)

    # Movement: the legal jumps from a square are 3 squares straight or 2 squares diagonally.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # If k is in square (i, j), then k + 1 is in one of the squares a legal jump away that is
    # still inside the grid.
    for k in 1:cells-1, i in 1:n, j in 1:n
        targets = [at[k+1, i+a, j+b] for (a, b) in moves if 1 <= i + a <= n && 1 <= j + b <= n]
        @constraint(model, at[k, i, j] <= sum(targets; init = 0))
    end

    # x[i, j] = the number written in square (i, j), the declared output; it is its own
    # bounded integer variable tied to the indicators so that enumeration cuts only these.
    @variable(model, 1 <= x[1:n, 1:n] <= cells, Int)
    @constraint(model, [i = 1:n, j = 1:n], x[i, j] == sum(k * at[k, i, j] for k in 1:cells))

    return model, Dict("x" => x)
end
