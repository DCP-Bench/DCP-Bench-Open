#!/usr/bin/python3
# Category: csplib
# Source and problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob013_progressive_party.py
# Source description: https://www.csplib.org/Problems/prob013/

# Data
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats
# End of data

# Import libraries
import json
from cpmpy import *
from cpmpy.expressions.utils import all_pairs


def progressive_party(n_boats, n_periods, capacity, crew_size, **kwargs):
    is_host = boolvar(shape=n_boats, name="is_host")
    visits = intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")

    model = Model()

    # Crews of host boats stay on boat
    for boat in range(n_boats):
        model += (is_host[boat]).implies((visits[:, boat] == boat).all())

    # Number of visitors can never exceed capacity of boat
    for slot in range(n_periods):
        for boat in range(n_boats):
            model += sum((visits[slot] == boat) * crew_size) <= capacity[boat]

    # Guests cannot visit a boat twice
    for boat in range(n_boats):
        model += (~is_host[boat]).implies(AllDifferent(visits[:, boat]))

    # Non-host boats cannot be visited
    for boat in range(n_boats):
        model += (~is_host[boat]).implies((visits != boat).all())

    # Crews cannot meet more than once
    for c1, c2 in all_pairs(range(n_boats)):
        model += sum(visits[:, c1] == visits[:, c2]) <= 1

    # Minimize number of hosts needed
    model.minimize(sum(is_host))

    return model, (visits, is_host)


# Example usage
model, (visits, is_host) = progressive_party(n_boats, n_periods, capacity, crew_size)
model.solve()

# Print
solution = {
    "visits": visits.value().tolist(),
    "is_host": is_host.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
