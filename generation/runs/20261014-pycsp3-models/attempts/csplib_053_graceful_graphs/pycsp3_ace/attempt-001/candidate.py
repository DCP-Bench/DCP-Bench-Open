from pycsp3 import *

# Graceful labelling: the graph has n nodes and m edges. Each node gets a distinct
# label from 0 to m, and each edge xy is labelled with |f(x) - f(y)|, and these edge
# labels must all be different.

n = data.n
m = data.m
graph = data.graph

# nodes[i] is the label f(i) of node i
nodes = VarArray(size=n, dom=range(0, m + 1))
# edges[k] is the label of edge k, which joins the nodes graph[k][0] and graph[k][1]
edges = VarArray(size=m, dom=range(1, m + 1))

satisfy(
    # each node has a unique label
    AllDifferent(nodes),

    # the label of each edge is the difference of the labels of its two nodes
    [edges[k] == abs(nodes[graph[k][0]] - nodes[graph[k][1]]) for k in range(m)],

    # the edge labels are all different
    AllDifferent(edges),
)
