# Hidato: fill a grid with the numbers 1..r*c, each used once, so that the given numbers
# stay where they are and consecutive numbers sit in cells that touch horizontally,
# vertically or diagonally.
using JuMP

function build(instance)
    puzzle = instance["puzzle"]       # puzzle[i][j] = given number, or 0 for an empty cell
    r = length(puzzle)
    c = length(puzzle[1])
    N = r * c                         # numbers 1..N fill the grid

    model = Model()

    # at[i, j, k] = 1 when cell (i, j) holds the number k; each cell holds one number and
    # each number is in one cell (all numbers different)
    @variable(model, at[1:r, 1:c, 1:N], Bin)
    @constraint(model, [i = 1:r, j = 1:c], sum(at[i, j, k] for k in 1:N) == 1)
    @constraint(model, [k = 1:N], sum(at[i, j, k] for i in 1:r, j in 1:c) == 1)

    # Given numbers stay where they are
    clues = [(i, j, puzzle[i][j]) for i in 1:r, j in 1:c if puzzle[i][j] > 0]
    for (i, j, k) in clues
        @constraint(model, at[i, j, k] == 1)
    end

    # Consecutive numbers touch: if cell (i, j) holds k, then k + 1 is in one of the (up to
    # eight) cells around it, and the other way round for k - 1. The cell itself is not
    # among its neighbours.
    around(i, j) = [(i + a, j + b) for a in -1:1 for b in -1:1
                    if (a != 0 || b != 0) && 1 <= i + a <= r && 1 <= j + b <= c]
    for i in 1:r, j in 1:c, k in 1:N-1
        @constraint(model, at[i, j, k] <= sum(at[p, q, k+1] for (p, q) in around(i, j)))
        @constraint(model, at[i, j, k+1] <= sum(at[p, q, k] for (p, q) in around(i, j)))
    end

    # Implied by the touching rule: numbers k apart sit at most k cells apart in a king's
    # walk, so number k cannot be in a cell farther than |k - k'| from a given number k'.
    # This only removes impossible values and speeds the search.
    for i in 1:r, j in 1:c, k in 1:N, (ci, cj, ck) in clues
        if max(abs(i - ci), abs(j - cj)) > abs(k - ck)
            @constraint(model, at[i, j, k] == 0)
        end
    end

    # x[i, j] = the number in cell (i, j) (declared output)
    x = [sum(k * at[i, j, k] for k in 1:N) for i in 1:r, j in 1:c]
    return model, Dict("x" => x)
end
