
import cpmpy as cp
import json

# Data
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# visits[p,b] = v means in period p, boat b visits boat v (0-based index)
visits = cp.intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")
# is_host[b] == 1 means boat b is a host boat
is_host = cp.boolvar(shape=n_boats, name="is_host")

# Constraints list
constraints = []

# 1) If a boat b visits boat j in any period, then j must be a host
for p in range(n_periods):
    for b in range(n_boats):
        for j in range(n_boats):
            # (visits[p,b] == j) -> is_host[j]
            constraints.append((visits[p, b] == j).implies(is_host[j]))

# 2) If a boat is a host, it stays on its own boat each period
for h in range(n_boats):
    for p in range(n_periods):
        constraints.append(is_host[h].implies(visits[p, h] == h))

# 3) A guest boat cannot revisit a host: for non-host boats, visits across periods are all different
for b in range(n_boats):
    for p1 in range(n_periods):
        for p2 in range(p1 + 1, n_periods):
            # if b is not a host then visits[p1,b] != visits[p2,b]
            constraints.append((~is_host[b]).implies(visits[p1, b] != visits[p2, b]))

# 4) Guest crews cannot meet more than once:
# For any pair of boats b1,b2 that are both guests, the number of periods
# where they visit the same host is <= 1
for b1 in range(n_boats):
    for b2 in range(b1 + 1, n_boats):
        meet_bools = []
        for p in range(n_periods):
            meet_bools.append(visits[p, b1] == visits[p, b2])
        constraints.append(((~is_host[b1]) & (~is_host[b2])).implies(cp.sum(meet_bools) <= 1))

# 5) Capacity constraints: for each period and each boat h, total people aboard <= capacity[h]
for p in range(n_periods):
    for h in range(n_boats):
        # host crew counts if h is a host
        host_crew = crew_size[h] * is_host[h]
        # sum of crews of guest boats visiting h in period p (exclude b==h to avoid double counting)
        visitors_sum = cp.sum([(visits[p, b] == h) * crew_size[b] for b in range(n_boats) if b != h])
        constraints.append(host_crew + visitors_sum <= capacity[h])

# Add all constraints to the model
model += constraints

# Objective: minimize the number of hosts
model.minimize(cp.sum(is_host))

# Solve and print
if model.solve():
    # Convert is_host booleans to 0/1 integers
    is_host_list = [int(is_host[i].value()) for i in range(n_boats)]
    visits_list = visits.value().tolist()
    solution = {'visits': visits_list, 'is_host': is_host_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
