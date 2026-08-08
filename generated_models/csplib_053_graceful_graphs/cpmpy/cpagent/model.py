import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Graceful graph labeling
# - 8 nodes, 16 edges
# - Node labels: unique values from {0, 1, ..., 16}
# - Edge labels: |f(x) - f(y)| for each edge xy, all different
# - Edge labels must be {1, 2, ..., 16} (since we have 16 edges)

# Input data
m = 16  # Number of edges
n = 8   # Number of nodes
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables
# Node labels: each node gets a unique label from {0, 1, ..., m}
node_labels = cp.intvar(0, m, shape=n, name="node_labels")

# Edge labels: absolute differences between connected nodes
edge_labels = cp.intvar(1, m, shape=m, name="edge_labels")

# Constraints
# 1. All node labels must be different
model += cp.AllDifferent(node_labels)

# 2. Edge labels are absolute differences of connected nodes
for i, (u, v) in enumerate(graph):
    model += edge_labels[i] == cp.abs(node_labels[u] - node_labels[v])

# 3. All edge labels must be different and cover {1, 2, ..., m}
model += cp.AllDifferent(edge_labels)

# Since we have m edges and edge labels must be from {1, 2, ..., m},
# and all different, they must be exactly {1, 2, ..., m}
for i in range(m):
    model += cp.Count(edge_labels, i+1) == 1

# Performance improvements: symmetry breaking
# Fix the smallest node label to 0 (since labels are from {0,1,...,m})
model += node_labels[0] == 0

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    node_solution = node_labels.value().tolist()
    edge_solution = edge_labels.value().tolist()
    
    solution = {
        "nodes": node_solution,
        "edges": edge_solution
    }
    
    # Verification
    def verify_solution(sol):
        """Verify the graceful graph solution independently"""
        nodes = sol["nodes"]
        edges = sol["edges"]
        
        # 1. Structural verification
        if len(nodes) != n or len(edges) != m:
            return False
        
        # 2. Logical verification
        # Check node labels are unique and in range [0, m]
        if len(set(nodes)) != len(nodes) or min(nodes) < 0 or max(nodes) > m:
            return False
        
        # Check edge labels are computed correctly
        for i, (u, v) in enumerate(graph):
            expected_edge_label = abs(nodes[u] - nodes[v])
            if edges[i] != expected_edge_label:
                return False
        
        # Check edge labels are unique and cover {1, 2, ..., m}
        if len(set(edges)) != len(edges) or set(edges) != set(range(1, m+1)):
            return False
        
        return True
    
    assert verify_solution(solution), "Solution verification failed!"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))