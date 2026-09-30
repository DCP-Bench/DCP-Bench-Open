# Quasigroup completion: complete a partly filled N x N Latin square, so that
# each of 1..N occurs once in every row and every column.
using JuMP

function build(instance)
    n = instance["N"]
    start = instance["start"]    # given entries, 0 where a cell is empty
    model = Model()
    @variable(model, has[1:n, 1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, :]) == 1)
    @constraint(model, [i = 1:n, v = 1:n], sum(has[i, :, v]) == 1)
    @constraint(model, [j = 1:n, v = 1:n], sum(has[:, j, v]) == 1)
    for i in 1:n, j in 1:n
        start[i][j] != 0 && fix(has[i, j, start[i][j]], 1; force = true)
    end
    @variable(model, 1 <= puzzle[1:n, 1:n] <= n, Int)
    @constraint(model, [i = 1:n, j = 1:n], puzzle[i, j] == sum(v * has[i, j, v] for v in 1:n))
    return model, Dict("puzzle" => puzzle)
end
