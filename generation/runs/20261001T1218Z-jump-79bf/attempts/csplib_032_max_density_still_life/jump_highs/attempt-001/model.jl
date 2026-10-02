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

    # The pairs (live neighbours, state of the cell) that keep a cell unchanged: a dead cell
    # with any number of neighbours except 3, and a live cell with 2 or 3 neighbours.
    # MOI.Table takes the tuples as a Float64 matrix, one tuple per row.
    pairs = [(k, 0) for k in 0:8 if k != 3]
    push!(pairs, (2, 1), (3, 1))
    stable = Float64[p[c] for p in pairs, c in 1:2]

    # In-grid cells: each cell and the number of live cells among its up to 8 neighbours
    # must be an allowed pair.
    for i in 1:n, j in 1:m
        neighbours = [grid[i+di, j+dj] for di in -1:1 for dj in -1:1
                      if (di != 0 || dj != 0) && 1 <= i + di <= n && 1 <= j + dj <= m]
        live_neighbours = @variable(model, lower_bound = 0, upper_bound = 8, integer = true)
        @constraint(model, live_neighbours == sum(neighbours))
        @constraint(model, [live_neighbours, grid[i, j]] in MOI.Table(stable))
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

    # as many live cells as possible
    @objective(model, Max, sum(grid))

    return model, Dict("grid" => grid)
end
