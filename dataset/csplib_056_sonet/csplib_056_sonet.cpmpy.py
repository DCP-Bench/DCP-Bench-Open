#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob056/models/Sonet.py.html
# Source description: https://www.csplib.org/Problems/prob056

"""
In the SONET problem, we are given a set of nodes and the traffic demand for each pair of nodes. The nodes are connected
by a set of rings. A node is installed on a ring using an add-drop multiplexer (ADM). For two nodes to communicate,
they must be on at least one common ring. Each ring has a capacity, limiting the number of nodes it can host. The
objective is to satisfy all communication demands while minimizing the total number of ADMs used.

Print the total number of ADMs used (total_adms), and the configuration of nodes on rings (ring_config) where
ring_config[k, i] is 1 if node i is on ring k, 0 otherwise.
"""

# Data
# Maximum number of rings available
r = 4
# Number of nodes (clients)
n = 10
# Demand matrix: demand[i][j] is the traffic between node i and j
demand = [[0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
          [1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
          [1, 1, 0, 1, 0, 0, 0, 0, 0, 0],
          [0, 1, 1, 0, 1, 0, 0, 0, 0, 0],
          [0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
          [0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
          [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
          [1, 0, 0, 0, 0, 1, 1, 0, 1, 0],
          [0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
          [0, 0, 0, 0, 1, 0, 0, 0, 1, 0]]
# Maximum number of nodes that each ring can accommodate
capacity_nodes = [3, 4, 5, 6]
# End of data

# Import libraries
import cpmpy as cp
import json
import numpy as np

# Model definition
model = cp.Model()

# Decision Variables
# ring_config[k, i] is 1 if node i is on ring k, 0 otherwise.
ring_config = cp.boolvar(shape=(r, n), name="ring_config")

# Constraints
# 1. Demand satisfaction: For every pair of nodes (i, j) with demand > 0,
#    they must share at least one ring.
for i in range(n):
    for j in range(i + 1, n):  # Iterate over unique pairs
        if demand[i][j] > 0:
            # Sum of (ring_config[k,i] AND ring_config[k,j]) over all rings k must be >= 1
            on_common_ring = ring_config[:, i] & ring_config[:, j]
            model += cp.sum(on_common_ring) >= 1

# 2. Ring capacity: The number of nodes on each ring cannot exceed its capacity.
for k in range(r):
    model += cp.sum(ring_config[k, :]) <= capacity_nodes[k]

# Objective: Minimize the total number of ADMs.
# One ADM is used for each assignment of a node to a ring.
total_adms = cp.sum(ring_config)
model.minimize(total_adms)

# Solve and print
if model.solve():
    solution = {
        "ring_config": ring_config.value().tolist(),
        "total_adms": int(model.objective_value())
    }
    print(json.dumps(solution))
else:
    print("No solution found.")