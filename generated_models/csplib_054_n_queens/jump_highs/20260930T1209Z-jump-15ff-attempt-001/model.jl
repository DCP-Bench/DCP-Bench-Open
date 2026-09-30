# N-queens: place n queens on an n x n board, one in each row, so that no two
# share a column or a diagonal. queens[i] is the column, 1..n, of the queen in row i.
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    # at[i, j] = 1 when the queen of row i stands in column j
    @variable(model, at[1:n, 1:n], Bin)
    @constraint(model, [i = 1:n], sum(at[i, :]) == 1)   # one queen per row
    @constraint(model, [j = 1:n], sum(at[:, j]) == 1)   # one per column
    # at most one queen on every diagonal, in both directions
    @constraint(model, [d = -(n - 1):(n - 1)], sum(at[i, i + d] for i in 1:n if 1 <= i + d <= n) <= 1)
    @constraint(model, [s = 2:2n], sum(at[i, s - i] for i in 1:n if 1 <= s - i <= n) <= 1)
    @variable(model, 1 <= queens[1:n] <= n, Int)
    @constraint(model, [i = 1:n], queens[i] == sum(j * at[i, j] for j in 1:n))
    return model, Dict("queens" => queens)
end
