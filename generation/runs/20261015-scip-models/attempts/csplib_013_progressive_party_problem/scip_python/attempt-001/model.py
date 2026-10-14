# Progressive party problem (CSPLib 013): at a yacht club, choose the fewest host boats so that
# every guest crew visits one host boat per period, no boat exceeds its capacity, and no two crews
# meet more than once.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n_boats"]
    periods = instance["n_periods"]
    capacity = instance["capacity"]
    crew = instance["crew_size"]
    boats = range(n)
    m = Model("progressive_party")

    # is_host[b] = 1 if boat b is a host boat
    is_host = {b: m.addVar(name=f"is_host[{b}]", vtype="B") for b in boats}
    # at[p,b,h] = 1 if in period p the crew of boat b is aboard host boat h
    at = {(p, b, h): m.addVar(name=f"at[{p},{b},{h}]", vtype="B")
          for p in range(periods) for b in boats for h in boats}
    # meet[p,i,j] = 1 if the crews of boats i and j are aboard the same host in period p
    meet = {(p, i, j): m.addVar(name=f"meet[{p},{i},{j}]", vtype="B")
            for p in range(periods) for i in boats for j in boats if i < j}

    for p in range(periods):
        for b in boats:
            # the crew of every boat is aboard exactly one boat in each period
            m.addCons(quicksum(at[p, b, h] for h in boats) == 1)
            # a crew can only be aboard a boat that is a host
            for h in boats:
                m.addCons(at[p, b, h] <= is_host[h])
            # a host crew stays on its own boat as hosts
            m.addCons(at[p, b, b] >= is_host[b])
            # a host crew does not leave its own boat
            for h in boats:
                if h != b:
                    m.addCons(at[p, b, h] <= 1 - is_host[b])

        # the total number of people aboard a host, including the host crew, must not exceed capacity
        for h in boats:
            m.addCons(quicksum(crew[b] * at[p, b, h] for b in boats) <= capacity[h])

    # crews that are aboard the same host in a period meet in that period
    for p in range(periods):
        for i in boats:
            for j in boats:
                if i < j:
                    for h in boats:
                        m.addCons(meet[p, i, j] >= at[p, i, h] + at[p, j, h] - 1)

    # two crews cannot meet more than once (this also keeps a guest from revisiting a host)
    for i in boats:
        for j in boats:
            if i < j:
                m.addCons(quicksum(meet[p, i, j] for p in range(periods)) <= 1)

    # minimise the number of host boats
    m.setObjective(quicksum(is_host[b] for b in boats), "minimize")

    # visits[p][b] = the boat that boat b visits in period p
    visits = [[quicksum(h * at[p, b, h] for h in boats) for b in boats] for p in range(periods)]
    # is_host[b] = 1 if boat b is a host boat
    host_flags = [is_host[b] for b in boats]
    return m, {"visits": visits, "is_host": host_flags}
