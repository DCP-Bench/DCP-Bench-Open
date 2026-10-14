# Progressive party: choose which yacht-club boats act as hosts and, for every period, which
# host each boat's crew visits, so that capacities hold, guests never revisit a host, no two
# crews meet twice, and as few boats as possible are hosts.
from exact import Exact


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]  # capacity[h] = most people that fit on boat h at once
    crew_size = instance["crew_size"]  # crew_size[b] = number of people in boat b's crew

    solver = Exact()

    # is_host[b] = 1 when boat b is a host boat
    is_host = [f"is_host_{b}" for b in range(n_boats)]
    for name in is_host:
        solver.addVariable(name, 0, 1)

    # visits[p][b] = the boat whose deck boat b's crew is on in period p (b itself for a host)
    visits = [[f"visits_{p}_{b}" for b in range(n_boats)] for p in range(n_periods)]
    # at[p][b][h] = 1 when visits[p][b] == h. Exact reasons about linear constraints only, so
    # "crew b is on boat h" needs this 0/1 indicator; boats are few, so the domain is small.
    at = [[[f"at_{p}_{b}_{h}" for h in range(n_boats)] for b in range(n_boats)]
          for p in range(n_periods)]
    for p in range(n_periods):
        for b in range(n_boats):
            solver.addVariable(visits[p][b], 0, n_boats - 1)
            for h in range(n_boats):
                solver.addVariable(at[p][b][h], 0, 1)
            # in each period a crew is on exactly one boat
            solver.addConstraint([(1, at[p][b][h]) for h in range(n_boats)], True, 1, True, 1)
            solver.addConstraint([(h, at[p][b][h]) for h in range(1, n_boats)] + [(-1, visits[p][b])],
                                 True, 0, True, 0)

    # the crew of a host boat stays on its own boat in every period
    for b in range(n_boats):
        for p in range(n_periods):
            solver.addConstraint([(1, at[p][b][b]), (-1, is_host[b])], True, 0)

    # the people aboard a boat in a period, its host crew and its guests, never exceed its capacity
    for p in range(n_periods):
        for h in range(n_boats):
            solver.addConstraint([(crew_size[b], at[p][b][h]) for b in range(n_boats)],
                                 False, 0, True, capacity[h])

    # a guest crew cannot visit the same boat twice (a host's crew only ever sits on its own
    # boat, so the limit only matters for the other boats h != b)
    for b in range(n_boats):
        for h in range(n_boats):
            if h != b:
                solver.addConstraint([(1, at[p][b][h]) for p in range(n_periods)], False, 0, True, 1)

    # boats that are not hosts cannot be visited (this includes their own crew staying put)
    for p in range(n_periods):
        for b in range(n_boats):
            for h in range(n_boats):
                solver.addConstraint([(1, at[p][b][h]), (-1, is_host[h])], False, 0, True, 0)

    # two crews can be on the same boat in at most one period. meet[p][c1][c2] must be 1 when
    # both are on the same boat h in period p; it is only bounded from below, since at most one
    # period may count and the solver is free to leave it 0 when the crews are apart.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            meet = [f"meet_{p}_{c1}_{c2}" for p in range(n_periods)]
            for p in range(n_periods):
                solver.addVariable(meet[p], 0, 1)
                for h in range(n_boats):
                    solver.addConstraint([(1, meet[p]), (-1, at[p][c1][h]), (-1, at[p][c2][h])],
                                         True, -1)
            solver.addConstraint([(1, name) for name in meet], False, 0, True, 1)

    # minimise the number of host boats
    objective = [(1, name) for name in is_host]
    return solver, {"visits": visits, "is_host": is_host}, ("minimize", objective)
