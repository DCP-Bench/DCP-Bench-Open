# Progressive party: choose as few host boats as possible and timetable which
# host every guest crew visits in each period, within boat capacities.
import z3


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # capacity[b]: most people that boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    # is_host[b] is true if boat b is a host boat.
    is_host = [z3.Bool(f"is_host_{b}") for b in boats]
    # visits[p][b] is the boat that the crew of boat b is aboard during period p
    # (its own boat if b is a host).
    visits = [[z3.Int(f"visits_{p}_{b}") for b in boats] for p in periods]
    # aboard[p][b][h] is true if the crew of boat b is aboard boat h in period p
    # (the same fact as visits[p][b] == h). The capacity, repeat-visit and meeting
    # rules below are counted over these Booleans with pseudo-Boolean constraints,
    # which Z3 handles better than sums of integer equalities.
    aboard = [[[z3.Bool(f"aboard_{p}_{b}_{h}") for h in boats] for b in boats] for p in periods]

    solver = z3.Solver()

    # A crew is always aboard some boat of the fleet.
    for p in periods:
        for b in boats:
            solver.add(visits[p][b] >= 0, visits[p][b] <= n_boats - 1)
            for h in boats:
                solver.add(aboard[p][b][h] == (visits[p][b] == h))

    # The crew of a host boat stays on its own boat in every period.
    for b in boats:
        for p in periods:
            solver.add(z3.Implies(is_host[b], aboard[p][b][b]))

    # The people aboard a boat in a period (all crews there) never exceed its capacity.
    for p in periods:
        for h in boats:
            solver.add(z3.PbLe([(aboard[p][b][h], crew_size[b]) for b in boats], capacity[h]))

    # A guest crew cannot visit the same host twice.
    for b in boats:
        for h in boats:
            solver.add(z3.Implies(z3.Not(is_host[b]),
                                  z3.AtMost(*[aboard[p][b][h] for p in periods], 1)))

    # Only host boats can be visited: nobody is aboard a non-host boat.
    for h in boats:
        for p in periods:
            for b in boats:
                solver.add(z3.Implies(z3.Not(is_host[h]), z3.Not(aboard[p][b][h])))

    # Two crews cannot meet more than once: they are on the same boat in at most one period.
    for c1 in boats:
        for c2 in range(c1 + 1, n_boats):
            solver.add(z3.AtMost(*[z3.And(aboard[p][c1][h], aboard[p][c2][h])
                                   for p in periods for h in boats], 1))

    # Implied constraints that help prove the minimum. Each period, the guest crews
    # fit on the hosts next to the host crews, so the room left on the hosts is at
    # least the total size of the guest crews.
    room_on_hosts = z3.Sum([z3.If(is_host[h], capacity[h] - crew_size[h], 0) for h in boats])
    guest_people = z3.Sum([z3.If(is_host[b], 0, crew_size[b]) for b in boats])
    solver.add(room_on_hosts >= guest_people)
    # A guest crew visits a different host in each period, so if any boat is a guest
    # there are at least n_periods hosts.
    n_hosts = z3.Sum([z3.If(h, 1, 0) for h in is_host])
    solver.add(z3.Implies(z3.Or([z3.Not(h) for h in is_host]), n_hosts >= n_periods))

    # Minimise the number of host boats.
    return solver, {"is_host": is_host, "visits": visits}, ("minimize", n_hosts)
