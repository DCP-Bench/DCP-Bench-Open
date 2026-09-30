# Maximal independent set: choose nodes no two of which are adjacent, such that
# every node left out has a chosen neighbour.
using JuMP

function build(instance)
    n = instance["n"]
    adjacency = instance["adjacency_list"]   # neighbours of each node, 1-based
    model = Model()
    @variable(model, nodes[1:n], Bin)
    for i in 1:n
        # no edge has both ends chosen
        for j in adjacency[i]
            i < j && @constraint(model, nodes[i] + nodes[j] <= 1)
        end
        # a node is chosen or has a chosen neighbour
        @constraint(model, nodes[i] + sum(nodes[j] for j in adjacency[i]) >= 1)
    end
    return model, Dict("nodes" => nodes)
end
