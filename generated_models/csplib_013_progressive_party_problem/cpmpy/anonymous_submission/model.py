# Import libraries
from cpmpy import *
import json

# Parameters
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats

# Decision Variables
is_host = boolvar(shape=n_boats, name="is_host")  # Whether a boat is a host
visits = intvar(0, n_boats-1, shape=(n_boats, n_periods), name="visits")  # visits[g][p] is host index visited by guest g in period p

# Model
model = Model()

# Constraint: a boat cannot visit itself
for g in range(n_boats):
    for p in range(n_periods):
        model += (visits[g,p] != g)

# Constraint: a guest can only visit hosts
for g in range(n_boats):
    for p in range(n_periods):
        model += is_host[visits[g,p]]

# Constraint: a guest cannot visit the same host more than once
for g in range(n_boats):
    model += (is_host[g]).implies(AllDifferent(visits[g]))

# Constraint: guest crews cannot meet more than once (no two guests visit same host in same period)
for h in range(n_boats):
    for p in range(n_periods):
        model += sum([(visits[g,p] == h) for g in range(n_boats)]) <= 1

# Constraint: capacity constraints for hosts
for h in range(n_boats):
    for p in range(n_periods):
        model += (sum([(visits[g,p] == h) * crew_size[g] for g in range(n_boats)]) + crew_size[h]) <= capacity[h]

# Constraint: if not host, must visit a different host each period
for g in range(n_boats):
    model += (~is_host[g]).implies(AllDifferent(visits[g]))

# Objective: minimize the number of host boats
model.minimize(sum(is_host))

# Solve
model.solve()

# Prepare solution in correct format
visit_schedule = []
for g in range(n_boats):
    if is_host[g].value():
        visit_schedule.append([0]*n_periods)  # Hosts don't visit others
    else:
        visit_schedule.append([visits[g,p].value()+1 for p in range(n_periods)])  # +1 to make indices 1-based

solution = {
    "is_host": [bool(val) for val in is_host.value().tolist()],
    "visits": visit_schedule
}
print(json.dumps(solution))