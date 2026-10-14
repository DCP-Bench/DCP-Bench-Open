from pycsp3 import *

# Progressive party: some boats are hosts, the crews of the other boats visit the
# host boats over several half-hour periods. Every boat has a capacity and a crew size.

capacity = data.capacity
crew = data.crew_size
n_boats = data.n_boats
n_periods = data.n_periods

# is_host[b] is 1 when boat b is a host
is_host = VarArray(size=n_boats, dom={0, 1})
# visits[p][b] is the boat that boat b visits in period p (a host boat visits itself)
visits = VarArray(size=[n_periods, n_boats], dom=range(n_boats))

satisfy(
    # a host boat stays at its own place in every period
    [imply(is_host[b] == 1, visits[p][b] == b) for p in range(n_periods) for b in range(n_boats)],

    # the crew of a guest boat visits a host boat in every period
    [imply(is_host[b] == 0, is_host[visits[p][b]] == 1) for p in range(n_periods) for b in range(n_boats)],

    # the people aboard a boat, host crew and guest crews, must not exceed its capacity
    [Sum(crew[g] * (visits[p][g] == b) for g in range(n_boats)) <= capacity[b]
     for p in range(n_periods) for b in range(n_boats)],

    # a guest boat cannot revisit a host
    [Or(is_host[g] == 1, Sum(visits[p][g] == h for p in range(n_periods)) <= 1)
     for g in range(n_boats) for h in range(n_boats)],

    # two crews cannot meet more than once
    [Sum(visits[p][i] == visits[p][j] for p in range(n_periods)) <= 1
     for i in range(n_boats) for j in range(i + 1, n_boats)],
)

# minimise the number of host boats
minimize(Sum(is_host))
