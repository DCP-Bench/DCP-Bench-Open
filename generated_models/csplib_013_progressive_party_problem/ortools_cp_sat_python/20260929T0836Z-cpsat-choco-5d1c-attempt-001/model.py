# Progressive party: some boats are chosen as hosts and stay put; every other
# (guest) crew visits one host per period. A boat can hold only its capacity
# in total crew, a guest never visits the same host twice, and two crews meet
# at most once. Minimise the number of host boats.
from ortools.sat.python import cp_model


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]  # people each boat can hold
    crew_size = instance["crew_size"]  # people in each boat's crew

    boats = range(n_boats)
    periods = range(n_periods)

    model = cp_model.CpModel()

    # is_host[b] is true when boat b is a host
    is_host = [model.new_bool_var(f"is_host_{b}") for b in boats]
    # visits[p][b] = the boat that boat b's crew is on in period p (b itself for a host)
    visits = [[model.new_int_var(0, n_boats - 1, f"visits_{p}_{b}") for b in boats] for p in periods]
    # at[p][b][h] is true when crew b is on boat h in period p (visits[p][b] == h)
    at = [[[model.new_bool_var(f"at_{p}_{b}_{h}") for h in boats] for b in boats] for p in periods]
    for p in periods:
        for b in boats:
            model.add_exactly_one(at[p][b])
            model.add(visits[p][b] == sum(h * at[p][b][h] for h in boats))

    for b in boats:
        # the crew of a host boat stays on board in every period
        for p in periods:
            model.add(visits[p][b] == b).only_enforce_if(is_host[b])

    # the crews on a boat never outnumber its capacity
    for p in periods:
        for h in boats:
            model.add(sum(crew_size[b] * at[p][b][h] for b in boats) <= capacity[h])

    for b in boats:
        # a guest crew never visits the same boat twice
        for h in boats:
            model.add(sum(at[p][b][h] for p in periods) <= 1).only_enforce_if(is_host[b].negated())
        # a boat that is not a host is never visited
        for p in periods:
            for c in boats:
                model.add(at[p][c][b] == 0).only_enforce_if(is_host[b].negated())

    # two crews are on the same boat in at most one period
    for c1 in boats:
        for c2 in range(c1 + 1, n_boats):
            together = []
            for p in periods:
                same = model.new_bool_var(f"together_{p}_{c1}_{c2}")
                model.add(visits[p][c1] == visits[p][c2]).only_enforce_if(same)
                model.add(visits[p][c1] != visits[p][c2]).only_enforce_if(same.negated())
                together.append(same)
            model.add(sum(together) <= 1)

    # use as few host boats as possible
    model.minimize(sum(is_host))

    return model, {"visits": visits, "is_host": is_host}
