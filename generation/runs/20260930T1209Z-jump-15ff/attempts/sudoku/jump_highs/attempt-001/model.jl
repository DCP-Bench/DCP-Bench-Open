# Sudoku: fill the grid with the digits 1..9 so that every row, every column and
# every 3 x 3 box holds each digit once, keeping the given digits (0 marks an
# empty cell).
using JuMP

function build(instance)
    given = instance["input_grid"]
    n = length(given)            # side of the grid
    b = isqrt(n)                 # side of a box
    model = Model()
    # has[i, j, v] = 1 when cell (i, j) holds v
    @variable(model, has[1:n, 1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, :]) == 1)
    @constraint(model, [i = 1:n, v = 1:n], sum(has[i, :, v]) == 1)   # rows
    @constraint(model, [j = 1:n, v = 1:n], sum(has[:, j, v]) == 1)   # columns
    @constraint(model, [r = 0:b-1, c = 0:b-1, v = 1:n],
                sum(has[r * b + i, c * b + j, v] for i in 1:b, j in 1:b) == 1)   # boxes
    # the given digits stay
    for i in 1:n, j in 1:n
        if given[i][j] != 0
            fix(has[i, j, given[i][j]], 1; force = true)
        end
    end
    @variable(model, 1 <= grid[1:n, 1:n] <= n, Int)
    @constraint(model, [i = 1:n, j = 1:n], grid[i, j] == sum(v * has[i, j, v] for v in 1:n))
    return model, Dict("grid" => grid)
end
