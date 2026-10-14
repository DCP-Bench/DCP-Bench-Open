# Progressive party: choose as few host boats as possible and timetable which
# host every guest crew visits in each period, within boat capacities.
import z3


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # capacity[b]: most people that boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: people in the crew of boat b

    # is_host[b] is true if boat b is a host boat.
    is_host = [z3.Bool(f"is_host_{b}") for b in range(n_boats)]
    # visits[p][b] is the boat that the crew of boat b is aboard during period p
    # (its own boat if b is a host).
    visits = [[z3.Int(f"visits_{p}_{b}") for b in range(n_boats)] for p in range(n_periods)]
    # aboard[p][b][h] is true if the crew of boat b is aboard boat h in period p
    # (shares the meaning of visits[p][b] == h and keeps the sums below linear).
    aboard = [[[z3.Bool(f"aboard_{p}_{b}_{h}") for h in range(n_boats)]
               for b in range(n_boats)] for p in range(n_periods)]

    solver = z3.Solver()

    # A crew is always aboard some boat of the fleet.
    for p in range(n_periods):
        for b in range(n_boats):
            solver.add(visits[p][b] >= 0, visits[p][b] <= n_boats - 1)
            for h in range(n_boats):
                solver.add(aboard[p][b][h] == (visits[p][b] == h))

    # The crew of a host boat stays on its own boat in every period.
    for b in range(n_boats):
        solver.add(z3.Implies(is_host[b], z3.And([visits[p][b] == b for p in range(n_periods)])))

    # The people aboard a boat in a period (all crews there) never exceed its capacity.
    for p in range(n_periods):
        for h in range(n_boats):
            solver.add(z3.Sum([z3.If(aboard[p][b][h], crew_size[b], 0)
                               for b in range(n_boats)]) <= capacity[h])

    # A guest crew cannot visit the same host twice.
    for b in range(n_boats):
        solver.add(z3.Implies(z3.Not(is_host[b]),
                              z3.Distinct([visits[p][b] for p in range(n_periods)])))

    # Only host boats can be visited: nobody is aboard a non-host boat.
    for h in range(n_boats):
        solver.add(z3.Implies(z3.Not(is_host[h]),
                              z3.Not(z3.Or([aboard[p][b][h]
                                            for p in range(n_periods) for b in range(n_boats)]))))

    # Two crews cannot meet more than once: they are on the same boat in at most one period.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            together = [z3.If(visits[p][c1] == visits[p][c2], 1, 0) for p in range(n_periods)]
            solver.add(z3.Sum(together) <= 1)

    # Minimise the number of host boats.
    n_hosts = z3.Sum([z3.If(h, 1, 0) for h in is_host])
    return solver, {"is_host": is_host, "visits": visits}, ("minimize", n_hosts)
