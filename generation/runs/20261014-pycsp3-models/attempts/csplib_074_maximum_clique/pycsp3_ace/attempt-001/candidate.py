# Maximum clique: choose a largest set of vertices of the graph in which every two vertices are adjacent.
from pycsp3 import *

n = data.n
adj = data.adj

# c[i] = 1 if vertex i is in the clique, else 0
c = VarArray(size=n, dom={0, 1})

satisfy(
    # two vertices that are not adjacent cannot both be in the clique
    [c[i] + c[j] <= 1 for i in range(n) for j in range(i + 1, n) if adj[i][j] == 0],
)

# maximise the number of vertices in the clique
maximize(Sum(c))
