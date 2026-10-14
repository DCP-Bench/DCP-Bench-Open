"""Progressive party: timetable a party at a yacht club with as few host boats as possible.

Some boats are hosts and their crews stay aboard. In each period the crew of
every other (guest) boat visits one host. A boat holds only so many people at a
time, crew sizes differ, a guest crew never visits the same host twice, and two
crews never meet in more than one period. Minimise the number of hosts.
"""
import pulp


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # most people aboard boat b at one time
    crew_size = instance["crew_size"]  # people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    problem = pulp.LpProblem("progressive_party", pulp.LpMinimize)

    # is_host[b] = 1 if boat b is a host (declared output)
    is_host = [pulp.LpVariable(f"is_host_{b}", cat="Binary") for b in boats]

    # at[p][b][h] = 1 if in period p the crew of boat b is aboard boat h.
    # A host's crew is aboard its own boat, so at[p][h][h] is the host's own stay.
    at = [[[pulp.LpVariable(f"at_{p}_{b}_{h}", cat="Binary") for h in boats]
           for b in boats] for p in periods]

    # visits[p][b] = the boat that the crew of boat b is aboard in period p
    # (declared output). Bounded integers tied to `at` by equality, so that
    # finding a second solution only cuts over these variables.
    visits = [[pulp.LpVariable(f"visits_{p}_{b}", 0, n_boats - 1, cat="Integer")
               for b in boats] for p in periods]

    # in every period each crew is aboard exactly one boat
    for p in periods:
        for b in boats:
            problem += pulp.lpSum(at[p][b]) == 1
            problem += visits[p][b] == pulp.lpSum(h * at[p][b][h] for h in boats)

    # the objective: minimise the number of host boats
    problem += pulp.lpSum(is_host)

    # the crew of a host boat stays on its boat in every period; a crew that is
    # not a host never stays on its own boat (it must visit someone else)
    for p in periods:
        for h in boats:
            problem += at[p][h][h] == is_host[h]

    # non-host boats cannot be visited
    for p in periods:
        for b in boats:
            for h in boats:
                problem += at[p][b][h] <= is_host[h]

    # the people aboard a boat in a period never exceed its capacity
    for p in periods:
        for h in boats:
            problem += pulp.lpSum(crew_size[b] * at[p][b][h] for b in boats) <= capacity[h]

    # a guest crew cannot visit the same boat twice (a host's own stay on its
    # boat is not a visit and is excluded)
    for b in boats:
        for h in boats:
            if h != b:
                problem += pulp.lpSum(at[p][b][h] for p in periods) <= 1

    # two crews cannot meet more than once: meet[p][a][b] is forced to 1 when the
    # crews of boats a and b are aboard the same boat in period p, and the number
    # of such periods is at most 1. One lower-bound row per boat suffices because
    # each crew is aboard exactly one boat.
    for a in boats:
        for b in range(a + 1, n_boats):
            meet = [pulp.LpVariable(f"meet_{p}_{a}_{b}", 0, 1) for p in periods]
            for p in periods:
                for h in boats:
                    problem += meet[p] >= at[p][a][h] + at[p][b][h] - 1
            problem += pulp.lpSum(meet) <= 1

    return problem, {"visits": visits, "is_host": is_host}
