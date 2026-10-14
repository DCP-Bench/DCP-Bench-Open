from pycsp3 import *

graph = data.graph
n = len(graph)
# celebrities[i] is 1 when person i is a celebrity
celebrities = VarArray(size=n, dom={0, 1})

satisfy(
    # at least one celebrity is present at the party
    Sum(celebrities) >= 1,
    # a celebrity is known by everybody else: a person who does not know i rules i out
    [celebrities[i] == 0 for i in range(n) for j in range(n) if j != i and graph[j][i] == 0],
    # a celebrity only knows other celebrities: if i knows j and i is a celebrity, j is a celebrity
    [celebrities[i] <= celebrities[j] for i in range(n) for j in range(n) if j != i and graph[i][j] == 1],
)
