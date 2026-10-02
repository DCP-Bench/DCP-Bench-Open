# Discrete tomography: a matrix of zeroes and ones is "x-rayed" along its rows and
# columns, giving the number of ones in each row and each column. Reconstruct a matrix
# that matches these counts.
using JuMP

function build(instance)
    row_sums = instance["row_sums"]   # number of ones in each row
    col_sums = instance["col_sums"]   # number of ones in each column
    r = length(row_sums)
    c = length(col_sums)

    model = Model()

    # matrix[i, j] is the 0/1 entry in row i and column j (declared output)
    @variable(model, matrix[1:r, 1:c], Bin)

    # each row i holds row_sums[i] ones
    @constraint(model, [i = 1:r], sum(matrix[i, j] for j in 1:c) == row_sums[i])
    # each column j holds col_sums[j] ones
    @constraint(model, [j = 1:c], sum(matrix[i, j] for i in 1:r) == col_sums[j])

    return model, Dict("matrix" => matrix)
end
