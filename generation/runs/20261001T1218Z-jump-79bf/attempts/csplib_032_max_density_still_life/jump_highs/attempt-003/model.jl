# Maximum density still life: in Conway's Game of Life, find the most densely populated
# stable pattern (a "still life") on an n x m grid; cells outside the grid are dead. A live
# cell needs exactly 2 or 3 live neighbours to survive, and a dead cell (also outside the
# grid) must not have exactly 3 live neighbours, or it would become alive.
using JuMP

function build(instance)
    n = instance["n"]   # rows of the grid
    m = instance["m"]   # columns of the grid

    model = Model()

    # grid[i, j] = 1 when cell (i, j) is alive (declared output)
    @variable(model, grid[1:n, 1:m], Bin)

    # In-grid cells. neighbours = the cells around (i, j) inside the grid (up to 8) and
    # around = how many of them are alive. The stable pairs (around, state of the cell) are:
    # a live cell with 2 or 3 live neighbours, a dead cell with any number except 3.
    # A dead cell with more than 3 live neighbours is "crowded": crowded[i, j] = 1 allows
    # around >= 4 (and forbids around <= 3), crowded[i, j] = 0 limits around to at most 2.
    # This is written out instead of using MOI.Table, which adds one binary per allowed
    # pair for every cell.
    crowded = @variable(model, [1:n, 1:m], Bin)
    for i in 1:n, j in 1:m
        neighbours = [grid[i+di, j+dj] for di in -1:1 for dj in -1:1
                      if (di != 0 || dj != 0) && 1 <= i + di <= n && 1 <= j + dj <= m]
        around = sum(neighbours)
        most = length(neighbours)
        # a live cell has at least 2 and at most 3 live neighbours
        @constraint(model, around >= 2 * grid[i, j])
        @constraint(model, around <= most - (most - 3) * grid[i, j])
        # a dead cell has at most 2 live neighbours, or at least 4 (crowded); the terms with
        # grid[i, j] switch both rules off for a live cell
        @constraint(model, around <= 2 + (most - 2) * crowded[i, j] + (most - 2) * grid[i, j])
        @constraint(model, around >= 4 * crowded[i, j])
    end

    # Dead cells just outside the grid must not have exactly 3 live neighbours either. Such
    # a cell sees up to three cells of the border row or column next to it, so three
    # consecutive live cells along an edge are not allowed.
    for j in 2:m-1
        @constraint(model, grid[1, j-1] + grid[1, j] + grid[1, j+1] <= 2)   # above the top row
        @constraint(model, grid[n, j-1] + grid[n, j] + grid[n, j+1] <= 2)   # below the bottom row
    end
    for i in 2:n-1
        @constraint(model, grid[i-1, 1] + grid[i, 1] + grid[i+1, 1] <= 2)   # left of the left column
        @constraint(model, grid[i-1, m] + grid[i, m] + grid[i+1, m] <= 2)   # right of the right column
    end

    # Implied limits on how dense a still life can be locally (a search over the stability
    # rules finds no still life with 7 live cells in a 3 x 3 block, or 5 in a 2 x 3 or
    # 3 x 2 block). They follow from the rules above and only tighten the relaxation.
    for i in 1:n-2, j in 1:m-2
        @constraint(model, sum(grid[i:i+2, j:j+2]) <= 6)
    end
    for i in 1:n-1, j in 1:m-2
        @constraint(model, sum(grid[i:i+1, j:j+2]) <= 4)
    end
    for i in 1:n-2, j in 1:m-1
        @constraint(model, sum(grid[i:i+2, j:j+1]) <= 4)
    end

    # as many live cells as possible
    @objective(model, Max, sum(grid))

    return model, Dict("grid" => grid)
end
