# Balanced incomplete block design (v, b, r, k, l): a v x b 0/1 matrix in which
# every row has r ones, every column has k ones, and every two rows have ones in
# exactly l common columns.
using JuMP

function build(instance)
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]
    model = Model()
    @variable(model, matrix[1:v, 1:b], Bin)
    @constraint(model, [i = 1:v], sum(matrix[i, :]) == r)
    @constraint(model, [j = 1:b], sum(matrix[:, j]) == k)
    # both[i1, i2, j] = matrix[i1, j] * matrix[i2, j], linearised
    for i1 in 1:v-1, i2 in i1+1:v
        both = @variable(model, [1:b], Bin)
        @constraint(model, [j = 1:b], both[j] <= matrix[i1, j])
        @constraint(model, [j = 1:b], both[j] <= matrix[i2, j])
        @constraint(model, [j = 1:b], both[j] >= matrix[i1, j] + matrix[i2, j] - 1)
        # the two rows share exactly l columns
        @constraint(model, sum(both) == l)
    end
    return model, Dict("matrix" => matrix)
end
