import json
from cpmpy import *
m = 16
n = 8
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7], [0, 4], [1, 5], [2, 6], [3, 7]]
nodes = intvar(0, m, shape=n, name='nodes')
edges = intvar(1, m, shape=m, name='edges')
model = Model()
model += AllDifferent(nodes)
model += AllDifferent(edges)
for idx, (left, right) in enumerate(graph):
    model += edges[idx] == abs(nodes[left] - nodes[right])
if not model.solve():
    raise RuntimeError('no graceful labelling found')
print(json.dumps({'nodes': nodes.value().tolist(), 'edges': edges.value().tolist()}))