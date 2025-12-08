#!/usr/bin/python3
# Category: csplib
# Source and problem instances: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob013_progressive_party.py
# Source description: https://www.csplib.org/Problems/prob013/

"""
The problem is to timetable a party at a yacht club. Certain boats are to be designated hosts, and the crews of the
remaining boats in turn visit the host boats for several successive half-hour periods. The crew of a host boat remains
on board to act as hosts while the crew of a guest boat together visits several hosts. Every boat can only hold a limited
number of people at a time (its capacity) and crew sizes are different. The total number of people aboard a boat,
including the host crew and guest crews, must not exceed the capacity. A guest boat cannot revisit a host and guest
crews cannot meet more than once. The problem facing the rally organizer is that of minimizing the number of host boats.

Print the visit schedule (visits) as a list of lists, where each inner list represents the boats visited - 0-based index - in each period,
e.g. visits[p,b] == v means that in period p, boat b visits boat v. Also print whether each boat is a host (is_host) as a list of booleans.
"""

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
