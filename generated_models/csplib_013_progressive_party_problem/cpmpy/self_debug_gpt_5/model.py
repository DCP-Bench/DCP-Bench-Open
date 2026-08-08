
import cpmpy as cp
import numpy as np
import json

# Data (optional)
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats
boats = range(n_boats)
periods = range(n_periods)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
visits = cp.intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")  # visits[p,b] = host visited by boat b in period p
is_host = cp.boolvar(shape=n_boats, name="is_host")  # 1 if boat is a host

# Constraints

# Hosts stay on their own boat each period; Non-hosts cannot stay on their boat
for b in boats:
    # If host, they stay on their own boat every period
    model += is_host[b].implies(cp.all([visits[p, b] == b for p in periods]))
    # If not host, they cannot be on their own boat
    model += (~is_host[b]).implies(cp.all([visits[p, b] != b for p in periods]))

# Visits must be to a host boat (including oneself if host)
for p in periods:
    for b in boats:
        for v in boats:
            model += (visits[p, b] == v).implies(is_host[v])

# A guest boat cannot revisit a host: all visits over periods must be different for guests
for b in boats:
    model += (~is_host[b]).implies(cp.all([visits[p1, b] != visits[p2, b] for p1 in periods for p2 in periods if p1 < p2]))

# Guest crews cannot meet more than once:
# For any pair of guest boats, they can be at the same host in at most one period
for b1 in boats:
    for b2 in boats:
        if b1 < b2:
            same_host_per_period = [visits[p, b1] == visits[p, b2] for p in periods]
            model += ((~is_host[b1]) & (~is_host[b2])).implies(cp.sum(same_host_per_period) <= 1)

# Capacity constraints: total people on a host boat in a period cannot exceed capacity
# This includes the host crew (counted via visits[p, h] == h) and all guest crews visiting h
for p in periods:
    for h in boats:
        # Sum of crew sizes of all boats visiting h in period p (including h if host)
        load = cp.sum([(visits[p, b] == h) * crew_size[b] for b in boats])
        model += load <= capacity[h]

# Objective: minimize the number of host boats
model.minimize(cp.sum(is_host))

# Solve and print
if model.solve():
    solution = {
        'visits': visits.value().tolist(),
        'is_host': np.array(is_host.value(), dtype=int).tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
