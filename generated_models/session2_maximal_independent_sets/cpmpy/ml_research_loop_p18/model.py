import json

n = 8
adjacency = [
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7],
]
edges = {
    tuple(sorted((node, neighbor - 1)))
    for node, neighbors in enumerate(adjacency)
    for neighbor in neighbors
}
best = None
for mask in range(1 << n):
    selected = {idx for idx in range(n) if mask & (1 << idx)}
    if any(left in selected and right in selected for left, right in edges):
        continue
    maximal = all(
        idx in selected
        or any((neighbor - 1) in selected for neighbor in adjacency[idx])
        for idx in range(n)
    )
    if maximal:
        if best is None or len(selected) > len(best):
            best = selected
print(json.dumps({"nodes": [idx in best for idx in range(n)]}))
