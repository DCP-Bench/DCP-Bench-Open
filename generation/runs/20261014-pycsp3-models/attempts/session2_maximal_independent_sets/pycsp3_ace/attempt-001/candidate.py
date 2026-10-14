from pycsp3 import *

# find a maximal independent set of the graph: no two chosen nodes are adjacent, and every other node
# is adjacent to a chosen node
n = data.n

# nodes[i] is 1 if node i + 1 is in the independent set; the adjacency list uses node numbers from 1
nodes = VarArray(size=n, dom={0, 1})

satisfy(
    # no two adjacent nodes are both in the set
    [nodes[i] + nodes[j - 1] <= 1 for i in range(n) for j in data.adjacency_list[i]],
    # a node outside the set must have a neighbour in the set, so the set cannot be extended
    [nodes[i] + Sum(nodes[j - 1] for j in data.adjacency_list[i]) >= 1 for i in range(n)],
)
