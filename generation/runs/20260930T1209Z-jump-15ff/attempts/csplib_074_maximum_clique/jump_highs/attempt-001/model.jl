# Maximum clique: the largest set of vertices of a graph that are pairwise adjacent.
using JuMP

function build(instance)
    n = instance["n"]
    adj = instance["adj"]
    model = Model()
    @variable(model, c[1:n], Bin)
    # two vertices without an edge are not both in the clique
    for i in 1:n-1, j in i+1:n
        adj[i][j] == 0 && @constraint(model, c[i] + c[j] <= 1)
    end
    @objective(model, Max, sum(c))
    return model, Dict("c" => c)
end
