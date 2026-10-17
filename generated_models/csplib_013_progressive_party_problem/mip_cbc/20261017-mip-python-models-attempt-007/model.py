# CSPLib 013, progressive party problem: timetable a party at a yacht club.
# Some boats are hosts; the crews of the other (guest) boats visit the host boats
# for several half-hour periods. The crew of a host boat stays on board. Capacity
# limits the people aboard, a guest boat cannot revisit a host, and crews cannot
# meet more than once. Minimise the number of host boats.
import mip


def build(instance):
    n = instance["n_boats"]
    periods = instance["n_periods"]
    cap = instance["capacity"]
    crew = instance["crew_size"]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # is_host[h] = 1 when boat h is a host boat.
    is_host = [m.add_var(f"host_{h}", var_type=mip.BINARY) for h in range(n)]
    # at[p][b][h] = 1 when crew b is aboard host boat h in period p.
    at = [
        [[m.add_var(f"at_{p}_{b}_{h}", var_type=mip.BINARY) for h in range(n)]
         for b in range(n)]
        for p in range(periods)
    ]

    # The crews of the remaining boats in turn visit the host boats for several
    # periods. The crew of a host boat remains on board to act as hosts.
    for p in range(periods):
        for b in range(n):
            # Every crew is aboard exactly one boat in each period.
            m.add_constr(mip.xsum(at[p][b][h] for h in range(n)) == 1)
            # The crew of a host boat remains on board, and a guest crew does not.
            m.add_constr(at[p][b][b] == is_host[b])
            # A guest crew visits only other host boats.
            for h in range(n):
                if h != b:
                    m.add_constr(at[p][b][h] <= 1 - is_host[b])

    # The total number of people aboard a boat, including the host crew and the
    # guest crews, must not exceed the capacity. A boat that is not a host holds nobody.
    for p in range(periods):
        for h in range(n):
            m.add_constr(
                mip.xsum(crew[b] * at[p][b][h] for b in range(n)) <= cap[h] * is_host[h]
            )
            # Crews go aboard host boats only, also when a crew size is zero.
            if min(crew) == 0:
                for b in range(n):
                    m.add_constr(at[p][b][h] <= is_host[h])

    # A guest boat cannot revisit a host.
    for b in range(n):
        for h in range(n):
            if h != b:
                m.add_constr(mip.xsum(at[p][b][h] for p in range(periods)) <= 1)

    # A guest visits several host boats, one in each period, so at least `periods`
    # hosts exist. Host capacities must also hold all the people, so enough
    # of the largest capacities must be hosts. Both are valid lower bounds on the hosts.
    total_people = sum(crew)
    kcap = n
    acc = 0
    for k, c in enumerate(sorted(cap, reverse=True), start=1):
        acc += c
        if acc >= total_people:
            kcap = k
            break
    m.add_constr(mip.xsum(is_host) >= max(min(n, periods), kcap))

    # Crews cannot meet more than once. Two crews meet when both are aboard the
    # same host boat in the same period. w is continuous: it is only pushed up by
    # the constraints, and the sum over periods and hosts stays at most 1.
    for a in range(n):
        for b in range(a + 1, n):
            meet = []
            for p in range(periods):
                for h in range(n):
                    w = m.add_var(f"meet_{p}_{a}_{b}_{h}", lb=0, ub=1)
                    m.add_constr(w >= at[p][a][h] + at[p][b][h] - 1)
                    meet.append(w)
            m.add_constr(mip.xsum(meet) <= 1)

    # The problem facing the rally organizer is that of minimizing the number of host boats.
    m.objective = mip.xsum(is_host)

    # visits[p][b] = the host boat that boat b visits in period p (0-based).
    visits = [
        [mip.xsum(h * at[p][b][h] for h in range(n)) for b in range(n)]
        for p in range(periods)
    ]

    return m, {"is_host": is_host, "visits": visits}
