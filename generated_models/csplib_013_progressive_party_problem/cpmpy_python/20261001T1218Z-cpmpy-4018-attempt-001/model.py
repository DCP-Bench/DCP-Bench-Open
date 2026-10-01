# Progressive party: some boats are chosen as hosts and stay put; every other
# (guest) crew visits one host per period. A boat can hold only its capacity
# in total crew, a guest never visits the same host twice, and two crews meet
# at most once. Minimise the number of host boats.
import cpmpy as cp


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]    # people each boat can hold
    crew_size = instance["crew_size"]  # people in each boat's crew

    # is_host[b] is true when boat b is a host
    is_host = cp.boolvar(shape=n_boats, name="is_host")
    # visits[p, b] = the boat that boat b's crew is on in period p (b itself for a host)
    visits = cp.intvar(0, n_boats - 1, shape=(n_periods, n_boats), name="visits")

    model = cp.Model()

    # The crew of a host boat stays on board in every period.
    for b in range(n_boats):
        model += is_host[b].implies((visits[:, b] == b).all())

    # The people on a boat in a period (its own crew if it hosts, plus the visiting crews)
    # never outnumber its capacity.
    for p in range(n_periods):
        for b in range(n_boats):
            model += cp.sum((visits[p, :] == b) * crew_size) <= capacity[b]

    # A guest crew never visits the same boat twice.
    for b in range(n_boats):
        model += (~is_host[b]).implies(cp.AllDifferent(visits[:, b]))

    # A boat that is not a host is never visited.
    for b in range(n_boats):
        model += (~is_host[b]).implies((visits != b).all())

    # Two crews are on the same boat in at most one period, so they meet at most once.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            model += cp.sum(visits[:, c1] == visits[:, c2]) <= 1

    # Use as few host boats as possible.
    model.minimize(cp.sum(is_host))

    return model, {"visits": visits, "is_host": is_host}
