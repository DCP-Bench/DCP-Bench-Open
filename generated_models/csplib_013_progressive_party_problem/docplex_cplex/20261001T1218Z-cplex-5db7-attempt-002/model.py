"""Progressive party: a yacht club party where some boats host and the other crews visit hosts.

In each period every crew is aboard one host boat. Host crews stay on their own boat.
Boat capacities limit the people aboard, a guest crew visits a host at most once, and two
crews are together in at most one period. The number of host boats is minimized.
"""
from docplex.mp.model import Model


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # capacity[b]: most people aboard boat b at a time
    crew_size = instance["crew_size"]  # crew_size[b]: people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    model = Model("progressive_party")
    # The meeting rule below is a quadratic constraint over binaries, which is not convex.
    # CPLEX refuses such a constraint unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # is_host[b] is 1 when boat b is a host boat.
    is_host = model.binary_var_list(n_boats, name="is_host")

    # at[p, c, b] is 1 when the crew of boat c is aboard boat b in period p.
    at = model.binary_var_cube(periods, boats, boats, name="at")

    # In every period each crew is aboard exactly one boat.
    for p in periods:
        for c in boats:
            model.add_constraint(model.sum(at[p, c, b] for b in boats) == 1)

    # Crews of host boats stay on their own boat in every period.
    for p in periods:
        for b in boats:
            model.add_constraint(at[p, b, b] >= is_host[b])

    # Only host boats can be visited. Summed over the crews of a period, so there is one
    # row per boat and period instead of one per crew (the model must stay small).
    for p in periods:
        for b in boats:
            model.add_constraint(model.sum(at[p, c, b] for c in boats) <= n_boats * is_host[b])

    # The people aboard a boat in a period never exceed its capacity.
    for p in periods:
        for b in boats:
            model.add_constraint(
                model.sum(crew_size[c] * at[p, c, b] for c in boats) <= capacity[b])

    # A guest crew cannot visit the same boat twice.
    for c in boats:
        for b in boats:
            if b != c:
                model.add_constraint(model.sum(at[p, c, b] for p in periods) <= 1)

    # Two crews cannot be together more than once: the number of (period, boat) pairs in
    # which both crews are aboard the same boat is at most 1. One quadratic constraint per
    # pair of crews; the linear alternative needs one row per pair, period and boat.
    for c1 in boats:
        for c2 in range(c1 + 1, n_boats):
            meetings = model.sum(at[p, c1, b] * at[p, c2, b] for p in periods for b in boats)
            model.add_constraint(meetings <= 1)

    # Minimize the number of host boats.
    model.minimize(model.sum(is_host))

    # visits[p][c] is the boat that the crew of boat c is aboard in period p.
    visits = [[model.sum(b * at[p, c, b] for b in boats) for c in boats] for p in periods]
    return model, {"visits": visits, "is_host": is_host}
