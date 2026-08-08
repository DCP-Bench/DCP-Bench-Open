
import cpmpy as cp
import json
import numpy as np

# Data
n_boats = 5  # Number of boats
n_periods = 4  # Number of periods
capacity = [6, 8, 12, 12, 12]  # Capacities of the boats
crew_size = [2, 2, 2, 2, 4]  # Crew sizes of the boats
# End of data

model = cp.Model()

# Decision variables
# is_host[i] = 1 if boat i is a host, else 0
is_host = cp.boolvar(shape=n_boats, name="is_host")

# visits[p, g] = h means guest boat g visits host boat h at period p
# Domain: 0..n_boats-1, but guest boats cannot visit themselves or non-hosts
# We will allow domain 0..n_boats-1, but constrain that if g is host, it does not visit anyone
# Also, guests cannot visit themselves
visits = cp.intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")

# Constraints

# 1) Hosts do not visit anyone (their visits are themselves or a dummy value)
for g in range(n_boats):
    # If g is host, then visits[p,g] == g (stay on own boat)
    for p in range(n_periods):
        model += (is_host[g].implies(visits[p, g] == g))
        # If not host, visits[p,g] != g (cannot visit self)
        model += (~is_host[g]).implies(visits[p, g] != g)

# 2) Only host boats can be visited
# For all visits[p,g], visits[p,g] must be a host boat
for p in range(n_periods):
    for g in range(n_boats):
        # visits[p,g] is a host
        # We use element constraint: is_host[visits[p,g]] == 1
        model += is_host[visits[p, g]] == 1

# 3) Capacity constraints: For each boat h and period p,
# sum of crew sizes of guests visiting h plus h's own crew size <= capacity[h]
for p in range(n_periods):
    for h in range(n_boats):
        # Guests visiting h at period p: those g with visits[p,g] == h and g != h
        # We create boolean variables for each g: guest_visits_h[p,h,g] = 1 if visits[p,g] == h
        guest_visits_h = [cp.boolvar() for _ in range(n_boats)]
        for g in range(n_boats):
            # guest_visits_h[g] == (visits[p,g] == h)
            model += guest_visits_h[g] == (visits[p, g] == h)
        # Sum crew sizes of guests visiting h excluding h itself (host)
        # So exclude g == h
        sum_guests = cp.sum([guest_visits_h[g] * crew_size[g] for g in range(n_boats) if g != h])
        # Total on boat h at period p = host crew size + sum guests
        model += sum_guests + crew_size[h] <= capacity[h]

# 4) A guest boat cannot revisit the same host more than once
# For each guest g, the visits over periods are all different (except for hosts who stay on their own boat)
for g in range(n_boats):
    # If g is not host, visits over periods are all different
    # If g is host, visits are all equal to g (already constrained)
    # So we only enforce all different if not host
    model += (~is_host[g]).implies(cp.AllDifferent([visits[p, g] for p in range(n_periods)]))

# 5) Guest crews cannot meet more than once
# For any two distinct guest boats g1 and g2, they cannot be on the same host boat at the same period more than once
# That means for all pairs (g1,g2), sum over p of (visits[p,g1] == visits[p,g2]) <= 1
# But only consider g1 != g2 and both not hosts (hosts stay on their own boat)
for g1 in range(n_boats):
    for g2 in range(g1 + 1, n_boats):
        # Only if both are guests (not hosts)
        model += (~is_host[g1] & ~is_host[g2]).implies(
            cp.sum([ (visits[p, g1] == visits[p, g2]) for p in range(n_periods)]) <= 1
        )

# 6) Minimize number of hosts
model.minimize(cp.sum(is_host))

# Solve and print
if model.solve():
    solution = {
        'visits': visits.value().tolist(),
        'is_host': [int(x) for x in is_host.value().tolist()]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
