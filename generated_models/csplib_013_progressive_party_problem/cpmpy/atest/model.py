# Data
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats

# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
# Decision Variables
is_host = boolvar(shape=n_boats, name="is_host")  # Whether a boat is a host
visits = intvar(-1, n_boats - 1, shape=(n_boats, n_periods), name="visits")  # Which host a boat visits in each period

# Model
model = Model()

# A boat cannot visit itself
model += [visits[i, p] != i for i in range(n_boats) for p in range(n_periods)]

# A boat cannot revisit a host
model += [AllDifferent([visits[i, p] for p in range(n_periods)]) for i in range(n_boats)]

# Hosts cannot visit any other boat
model += [visits[i, p] == -1 for i in range(n_boats) for p in range(n_periods) if is_host[i]]

# Capacity constraint: total people on a boat (host crew + guest crews) must not exceed capacity
for h in range(n_boats):
    for p in range(n_periods):
        guests = [visits[i, p] == h for i in range(n_boats)]
        total_people = crew_size[h] + sum(crew_size[i] * guests[i] for i in range(n_boats))
        model += [total_people <= capacity[h]]

# Solve
model.minimize(sum(is_host))

# Print
solution = {"is_host": is_host.value().tolist(), "visits": visits.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script