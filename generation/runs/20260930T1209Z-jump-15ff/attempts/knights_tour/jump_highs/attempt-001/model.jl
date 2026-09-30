# Knight's tour: move a knight over an n x n board so that it visits every
# square once (the tour need not return to its start). x[r, c] is the move, 0 to
# n*n - 1, on which the knight is on square (r, c).
using JuMP

function build(instance)
    n = instance["n"]
    cells = [(r, c) for r in 1:n for c in 1:n]
    nc = length(cells)
    jumps = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    neighbours = [[findfirst(==((r + dr, c + dc)), cells) for (dr, dc) in jumps
                   if 1 <= r + dr <= n && 1 <= c + dc <= n] for (r, c) in cells]
    model = Model()
    # on[k, q] = 1 when the knight stands on cell q at move k - 1
    @variable(model, on[1:nc, 1:nc], Bin)
    @constraint(model, [k = 1:nc], sum(on[k, :]) == 1)
    @constraint(model, [q = 1:nc], sum(on[:, q]) == 1)
    # the next move is a knight's jump away
    @constraint(model, [k = 1:nc-1, q = 1:nc], on[k, q] <= sum(on[k + 1, p] for p in neighbours[q]))
    @variable(model, 0 <= x[1:n, 1:n] <= nc - 1, Int)
    for (q, (r, c)) in enumerate(cells)
        @constraint(model, x[r, c] == sum((k - 1) * on[k, q] for k in 1:nc))
    end
    return model, Dict("x" => x)
end
