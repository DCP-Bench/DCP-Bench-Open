# Progressive party: at a yacht club some boats are hosts and stay put; the
# crews of the other boats visit one host in each period. Boats have limited
# capacity, a guest crew never revisits a host, two crews never meet twice,
# and the number of host boats is to be minimised.
from hermax.model import Model


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]  # most people a boat can hold at a time
    crew_size = instance["crew_size"]  # people in each boat's crew

    m = Model()
    # is_host[b] = boat b is a host boat
    is_host = m.bool_vector("is_host", n_boats)
    # visits[p][b] = the boat that the crew of boat b is on in period p
    # (domain 0..n_boats-1, as in the problem statement: boats are numbered from 0)
    visits = m.int_matrix("visits", n_periods, n_boats, 0, n_boats - 1)

    # the crew of a host boat stays on board in every period
    for b in range(n_boats):
        for p in range(n_periods):
            m &= (~is_host[b] | (visits[p][b] == b))

    # the people aboard a boat in a period, host crew included, never exceed its capacity
    for p in range(n_periods):
        for b in range(n_boats):
            m &= (sum(crew_size[g] * (visits[p][g] == b) for g in range(n_boats)) <= capacity[b])

    # a guest crew cannot visit the same boat in two different periods
    for b in range(n_boats):
        for v in range(n_boats):
            for p in range(n_periods):
                for q in range(p + 1, n_periods):
                    m &= (is_host[b] | ~(visits[p][b] == v) | ~(visits[q][b] == v))

    # a boat that is not a host cannot be visited by any crew
    for b in range(n_boats):
        for p in range(n_periods):
            for g in range(n_boats):
                m &= (is_host[b] | ~(visits[p][g] == b))

    # two crews cannot meet more than once. They meet in a period when they are
    # on the same boat; meet[c1][c2][p] is forced true by that, and at most one
    # period per pair of crews may have it true. Forcing in one direction is
    # enough because the flag is only ever bounded from above.
    for c1 in range(n_boats):
        for c2 in range(c1 + 1, n_boats):
            meet = m.bool_vector(f"meet_{c1}_{c2}", n_periods)
            for p in range(n_periods):
                for v in range(n_boats):
                    m &= (~(visits[p][c1] == v) | ~(visits[p][c2] == v) | meet[p])
            m &= meet.at_most_one()

    # minimise the number of host boats: a boat that is not a host pays nothing
    # and a host pays one, so the soft clause is broken exactly by a host
    # (soft clauses pay when their literal is false, hence the negation)
    for b in range(n_boats):
        m.obj[1] += ~is_host[b]

    return m, {"visits": visits, "is_host": is_host}
