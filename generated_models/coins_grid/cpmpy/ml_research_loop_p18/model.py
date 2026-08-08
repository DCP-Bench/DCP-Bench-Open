import json
from collections import deque
n = 31
coins_per_line = 14
node_count = 1 + n + n + 1
source = 0
sink = node_count - 1
graph = [[] for _ in range(node_count)]
def add_edge(left, right, capacity, cost):
    graph[left].append([right, capacity, cost, len(graph[right])])
    graph[right].append([left, 0, -cost, len(graph[left]) - 1])
for row in range(n):
    add_edge(source, 1 + row, coins_per_line, 0)
for row in range(n):
    for col in range(n):
        add_edge(1 + row, 1 + n + col, 1, (row - col) ** 2)
for col in range(n):
    add_edge(1 + n + col, sink, coins_per_line, 0)
flow = 0
z = 0
target_flow = n * coins_per_line
while flow < target_flow:
    dist = [10 ** 12 for _ in range(node_count)]
    parent = [None for _ in range(node_count)]
    in_queue = [False for _ in range(node_count)]
    dist[source] = 0
    queue = deque([source])
    in_queue[source] = True
    while queue:
        left = queue.popleft()
        in_queue[left] = False
        for edge_idx, edge in enumerate(graph[left]):
            right, capacity, cost, _ = edge
            if capacity <= 0 or dist[left] + cost >= dist[right]:
                continue
            dist[right] = dist[left] + cost
            parent[right] = (left, edge_idx)
            if not in_queue[right]:
                queue.append(right)
                in_queue[right] = True
    if parent[sink] is None:
        raise RuntimeError('no coins grid flow found')
    augment = target_flow - flow
    node = sink
    while node != source:
        left, edge_idx = parent[node]
        augment = min(augment, graph[left][edge_idx][1])
        node = left
    node = sink
    while node != source:
        left, edge_idx = parent[node]
        edge = graph[left][edge_idx]
        edge[1] -= augment
        graph[node][edge[3]][1] += augment
        z += augment * edge[2]
        node = left
    flow += augment
x = [[0 for _ in range(n)] for _ in range(n)]
for row in range(n):
    for right, capacity, _, _ in graph[1 + row]:
        if 1 + n <= right < 1 + 2 * n and capacity == 0:
            x[row][right - (1 + n)] = 1
print(json.dumps({'x': x, 'z': z}))