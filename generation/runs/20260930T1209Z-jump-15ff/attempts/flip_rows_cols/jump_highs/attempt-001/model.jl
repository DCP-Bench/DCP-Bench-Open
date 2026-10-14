# Flip rows and columns: choose a sign for every row and every column so that
# every row sum and every column sum of the signed matrix is non-negative, with
# the smallest possible total.
using JuMP

function build(instance)
    matrix = instance["input_matrix"]
    r, c = length(matrix), length(matrix[1])
    model = Model()
    @variable(model, row_flip[1:r], Bin)
    @variable(model, col_flip[1:c], Bin)
    # a cell changes sign when its row or its column, not both, is flipped
    @variable(model, cell[1:r, 1:c], Bin)
    for i in 1:r, j in 1:c
        @constraint(model, cell[i, j] >= row_flip[i] - col_flip[j])
        @constraint(model, cell[i, j] >= col_flip[j] - row_flip[i])
        @constraint(model, cell[i, j] <= row_flip[i] + col_flip[j])
        @constraint(model, cell[i, j] <= 2 - row_flip[i] - col_flip[j])
    end
    value(i, j) = matrix[i][j] * (1 - 2 * cell[i, j])
    # every row and column sum lies in 0..300, the total in 0..1000
    @constraint(model, [i = 1:r], 0 <= sum(value(i, j) for j in 1:c) <= 300)
    @constraint(model, [j = 1:c], 0 <= sum(value(i, j) for i in 1:r) <= 300)
    total = sum(value(i, j) for i in 1:r, j in 1:c)
    @constraint(model, 0 <= total <= 1000)
    @objective(model, Min, total)
    # the signs, +1 or -1
    @variable(model, -1 <= row_signs[1:r] <= 1, Int)
    @variable(model, -1 <= col_signs[1:c] <= 1, Int)
    @constraint(model, [i = 1:r], row_signs[i] == 1 - 2 * row_flip[i])
    @constraint(model, [j = 1:c], col_signs[j] == 1 - 2 * col_flip[j])
    return model, Dict("row_signs" => row_signs, "col_signs" => col_signs)
end
