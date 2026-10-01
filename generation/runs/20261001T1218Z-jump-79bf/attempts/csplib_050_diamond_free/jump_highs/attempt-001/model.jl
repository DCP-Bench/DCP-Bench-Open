# Diamond-free graphs: find a simple undirected graph on N vertices, given by its
# 0/1 adjacency matrix, with no isolated vertex, every degree a multiple of 3, a
# degree sum that is a multiple of 12, and no diamond (no four vertices with
# five or more edges among them).
using JuMP

function build(instance)
    N = instance["N"]   # number of vertices
    model = Model()

    # matrix[i, j] = 1 when vertices i and j are adjacent
    @variable(model, matrix[1:N, 1:N], Bin)

    # undirected graph without loops: symmetric with an empty diagonal
    @constraint(model, [i = 1:N, j = i+1:N], matrix[i, j] == matrix[j, i])
    @constraint(model, [i = 1:N], matrix[i, i] == 0)

    # degree[i] = number of neighbours of vertex i; it is a positive multiple of 3,
    # so degree[i] = 3 * k[i] with k[i] >= 1 (k[i] <= (N - 1) / 3 as the degree is at most N - 1)
    @variable(model, 1 <= k[1:N] <= div(N - 1, 3), Int)
    @constraint(model, [i = 1:N], sum(matrix[i, :]) == 3 * k[i])

    # the sum of the matrix (twice the number of edges) is a multiple of 12;
    # it is at most N * (N - 1)
    @variable(model, 0 <= m <= div(N * (N - 1), 12), Int)
    @constraint(model, sum(matrix) == 12 * m)

    # no diamond: among any four vertices there are at most four edges
    for a in 1:N-3, b in a+1:N-2, c in b+1:N-1, d in c+1:N
        @constraint(model, matrix[a, b] + matrix[a, c] + matrix[a, d] +
                           matrix[b, c] + matrix[b, d] + matrix[c, d] <= 4)
    end

    return model, Dict("matrix" => matrix)
end
