# Progressive party: choose the fewest host boats so that, in every period, each
# guest crew visits one host, no host is over capacity, and no two crews meet twice.
from pychoco.model import Model


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]  # capacity[h] = most people allowed aboard boat h
    crew_size = instance["crew_size"]  # crew_size[b] = number of people in the crew of boat b

    model = Model()

    # is_host[b] = 1 if boat b is a host boat
    is_host = [model.boolvar(name=f"is_host_{b}") for b in range(n_boats)]
    # visits[p][b] = the boat that the crew of boat b is aboard in period p
    visits = [[model.intvar(0, n_boats - 1, name=f"visits_{p}_{b}") for b in range(n_boats)]
              for p in range(n_periods)]
    # at[p][b][h] = 1 if the crew of boat b is aboard boat h in period p
    at = [[[model.arithm(visits[p][b], "=", h).reify() for h in range(n_boats)]
           for b in range(n_boats)] for p in range(n_periods)]

    # crews of host boats stay on their own boat in every period
    for b in range(n_boats):
        for p in range(n_periods):
            model.arithm(is_host[b], "<=", at[p][b][b]).post()

    # the number of people aboard a boat can never exceed its capacity: in each period
    # the boats' crews are packed into the boats they are aboard (bin packing, which
    # prunes more than a plain sum per boat)
    for p in range(n_periods):
        load = [model.intvar(0, capacity[h], name=f"load_{p}_{h}") for h in range(n_boats)]
        model.bin_packing(visits[p], crew_size, load).post()

    # non-host boats cannot be visited: nobody is aboard boat h unless h is a host
    for p in range(n_periods):
        for b in range(n_boats):
            for h in range(n_boats):
                model.arithm(at[p][b][h], "<=", is_host[h]).post()

    # a guest crew cannot visit the same boat twice. A guest never stays on its
    # own boat, so this is: for each other boat h, crew b is aboard h in at most
    # one period (a host crew never leaves its boat, so it satisfies this too).
    for b in range(n_boats):
        for h in range(n_boats):
            if h != b:
                model.sum([at[p][b][h] for p in range(n_periods)], "<=", 1).post()

    # two crews cannot meet more than once: they share a boat in at most one period
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            meet = [model.arithm(visits[p][c1], "=", visits[p][c2]).reify() for p in range(n_periods)]
            model.sum(meet, "<=", 1).post()

    # Implied constraints that help the solver bound the number of hosts:
    # (1) in every period all crews are aboard hosts, so the hosts' capacities must
    #     hold the people of all boats;
    model.scalar(is_host, capacity, ">=", sum(crew_size)).post()
    # (2) a guest crew visits a different host in every period, so with any guest
    #     there are at least n_periods hosts; with no guest every boat is a host.
    n_hosts = model.intvar(min(n_periods, n_boats), n_boats, name="n_hosts")

    # minimise the number of host boats (Choco optimises a single variable)
    model.sum(is_host, "=", n_hosts).post()

    return model, {"visits": visits, "is_host": is_host}, ("minimize", n_hosts)
