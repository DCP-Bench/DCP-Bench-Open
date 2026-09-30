# Graceful graph: label the n nodes of a graph with m edges with distinct numbers
# from 0..m so that the labels of the edges, the absolute differences of the
# labels of their ends, are distinct (they are 1..m).
using JuMP

function build(instance)
    m = instance["m"]
    n = instance["n"]
    graph = instance["graph"]     # edges as pairs of 0-based node numbers
    model = Model()
    @variable(model, 0 <= nodes[1:n] <= m, Int)
    @variable(model, 1 <= edges[1:m] <= m, Int)
    @constraint(model, nodes in MOI.AllDifferent(n))
    @constraint(model, edges in MOI.AllDifferent(m))
    # edges[e] = |u - v|: at least both differences, and at most one of them as
    # the binary side chooses
    @variable(model, side[1:m], Bin)
    for e in 1:m
        u, v = nodes[graph[e][1] + 1], nodes[graph[e][2] + 1]
        @constraint(model, edges[e] >= u - v)
        @constraint(model, edges[e] >= v - u)
        @constraint(model, edges[e] <= u - v + 2m * side[e])
        @constraint(model, edges[e] <= v - u + 2m * (1 - side[e]))
    end
    return model, Dict("nodes" => nodes, "edges" => edges)
end
