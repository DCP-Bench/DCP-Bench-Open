# Killer sudoku: a sudoku whose cages (groups of cells) add up to given totals,
# with no digit repeated inside a cage.
using JuMP

function build(instance)
    n = instance["n"]               # side of the grid
    cages = instance["problem"]     # [total, [[row, col], ...]], 1-based
    b = isqrt(n)
    model = Model()
    @variable(model, has[1:n, 1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, :]) == 1)
    @constraint(model, [i = 1:n, v = 1:n], sum(has[i, :, v]) == 1)
    @constraint(model, [j = 1:n, v = 1:n], sum(has[:, j, v]) == 1)
    @constraint(model, [r = 0:b-1, c = 0:b-1, v = 1:n],
                sum(has[r * b + i, c * b + j, v] for i in 1:b, j in 1:b) == 1)
    @variable(model, 1 <= x[1:n, 1:n] <= n, Int)
    @constraint(model, [i = 1:n, j = 1:n], x[i, j] == sum(v * has[i, j, v] for v in 1:n))
    # each cage adds up to its total with different digits
    for cage in cages
        total, cells = cage[1], cage[2]
        @constraint(model, sum(x[cell[1], cell[2]] for cell in cells) == total)
        @constraint(model, [v = 1:n], sum(has[cell[1], cell[2], v] for cell in cells) <= 1)
    end
    return model, Dict("x" => x)
end
