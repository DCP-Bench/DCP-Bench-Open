import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Find a maximal independent set in a graph
# - Independent set: no two vertices are adjacent
# - Maximal: cannot add any more vertices without violating independence
# - Output: binary array indicating which nodes are in the set

# Input data
n = 8  # number of nodes in the graph 
adjacency_list = [  # adjacency list for each node in the graph     
    [2, 3, 7],     
    [1, 4, 8],     
    [1, 4, 5],     
    [2, 3, 6],     
    [3, 6, 7],     
    [4, 5, 8],     
    [1, 5, 8],     
    [2, 6, 7] 
]

# Convert to 0-based indexing for internal processing
adj_0based = []
for i in range(n):
    adj_0based.append([x-1 for x in adjacency_list[i]])

# Pre-compute all edges for constraint generation
edges = []
for i in range(n):
    for j in adj_0based[i]:
        if i < j:  # avoid duplicates
            edges.append((i, j))

# Step 2: Model with CPMpy
# Decision variables: x[i] = 1 if node i is in the independent set
x = cp.boolvar(shape=n, name="nodes")

model = cp.Model()

# Constraint 1: Independence - no two adjacent nodes can both be in the set
for i, j in edges:
    model += x[i] + x[j] <= 1

# Constraint 2: Maximality - for each node not in the set, 
# at least one of its neighbors must be in the set
# This ensures we cannot add any more nodes
for i in range(n):
    # If node i is not selected (x[i] == 0), then at least one neighbor must be selected
    neighbors = adj_0based[i]
    if neighbors:  # only if node has neighbors
        model += (x[i] == 0).implies(cp.sum([x[j] for j in neighbors]) >= 1)

# Step 3: Solve and verify
# This is a satisfaction problem (any maximal independent set is valid)
if model.solve():
    solution_values = x.value()
    
    # Verification
    def verify_solution(nodes_binary, adjacency_list, n):
        """Verify that the solution is a valid maximal independent set"""
        # Convert adjacency list to 0-based for verification
        adj_0based = []
        for i in range(n):
            adj_0based.append([x-1 for x in adjacency_list[i]])
        
        selected = [i for i in range(n) if nodes_binary[i] == 1]
        not_selected = [i for i in range(n) if nodes_binary[i] == 0]
        
        # 1. Structural Verification
        if len(nodes_binary) != n:
            return False, f"Wrong number of nodes: got {len(nodes_binary)}, expected {n}"
        
        if not all(x in [0, 1] for x in nodes_binary):
            return False, "All values must be 0 or 1"
        
        # 2. Independence Verification
        # Check that no two selected nodes are adjacent
        for i in selected:
            for j in selected:
                if i != j and j in adj_0based[i]:
                    return False, f"Nodes {i} and {j} are both selected but are adjacent"
        
        # 3. Maximality Verification
        # For each non-selected node, check that it has at least one selected neighbor
        for i in not_selected:
            neighbors = adj_0based[i]
            if neighbors:  # only check nodes that have neighbors
                selected_neighbors = [j for j in neighbors if j in selected]
                if not selected_neighbors:
                    return False, f"Node {i} is not selected but has no selected neighbors: {neighbors}"
        
        return True, "Valid maximal independent set"
    
    # Test the solution
    solution_binary = [int(x) for x in solution_values]
    valid, msg = verify_solution(solution_binary, adjacency_list, n)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    solution = {
        "nodes": solution_binary
    }
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))