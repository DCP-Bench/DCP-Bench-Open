# Resource-constrained project scheduling: determine the start time of each job so that
# the total project duration (makespan) is minimised, while every precedence constraint
# holds and every resource's capacity is respected at every time.
import mip


def _sgs(order, dur, need, cap, preds, horizon):
    # Serial schedule generation: place the jobs in the given order, each at its earliest
    # start after its predecessors that keeps every resource within capacity.
    R = len(cap)
    use = [[0] * R for _ in range(horizon)]
    n = len(dur)
    st = [0] * n
    fin = [0] * n
    for i in order:
        t = max([fin[p] for p in preds[i]], default=0)
        while not _fits(use, t, dur[i], need[i], cap):
            t += 1
        for tau in range(t, t + dur[i]):
            for k in range(R):
                use[tau][k] += need[i][k]
        st[i] = t
        fin[i] = t + dur[i]
    return st, max(fin, default=0)


def _fits(use, t, d, r, cap):
    for tau in range(t, t + d):
        row = use[tau]
        for k in range(len(cap)):
            if row[k] + r[k] > cap[k]:
                return False
    return True


def _backward(st, makespan, dur, need, cap, succs, horizon):
    # Backward pass: place the jobs from the end, each as late as its successors and the
    # makespan allow. Returns None if a job cannot be placed at a time >= 0.
    n = len(dur)
    R = len(cap)
    use = [[0] * R for _ in range(horizon)]
    new = [None] * n
    remaining = set(range(n))
    while remaining:
        eligible = [i for i in remaining if all(new[s] is not None for s in succs[i])]
        i = max(eligible, key=lambda j: (st[j] + dur[j], st[j], j))
        t = min([new[s] for s in succs[i]], default=makespan) - dur[i]
        while t >= 0 and not _fits(use, t, dur[i], need[i], cap):
            t -= 1
        if t < 0:
            return None
        for tau in range(t, t + dur[i]):
            for k in range(R):
                use[tau][k] += need[i][k]
        new[i] = t
        remaining.discard(i)
    return new


def _heuristic_makespan(dur, need, cap, preds, succs, succ_pairs, horizon):
    # Deterministic upper bound: a serial schedule from the activity list in longest-tail
    # order, improved by forward-backward passes, then by first-improvement shifts of one
    # activity to another list position (positions scanned in a fixed order, no randomness).
    n = len(dur)
    tail = list(dur)
    for _ in range(n):
        for a, b in succ_pairs:
            tail[a] = max(tail[a], dur[a] + tail[b])

    def topo_ok(lst):
        pos = {j: idx for idx, j in enumerate(lst)}
        return all(pos[a] < pos[b] for a, b in succ_pairs)

    def evaluate(lst):
        st, M = _sgs(lst, dur, need, cap, preds, horizon)
        while True:
            topo = {j: idx for idx, j in enumerate(lst)}
            new = _backward(st, M, dur, need, cap, succs, horizon)
            if new is None:
                break
            order = sorted(range(n), key=lambda j: (new[j], topo[j]))
            st2, M2 = _sgs(order, dur, need, cap, preds, horizon)
            if M2 >= M:
                break
            st, M = st2, M2
            lst = order
        return M

    # Initial activity list: a precedence-feasible order, longest tail first, lower index first.
    indeg = [len(preds[i]) for i in range(n)]
    avail = [i for i in range(n) if indeg[i] == 0]
    lst = []
    while avail:
        i = max(avail, key=lambda j: (tail[j], -j))
        avail.remove(i)
        lst.append(i)
        for s in succs[i]:
            indeg[s] -= 1
            if indeg[s] == 0:
                avail.append(s)

    best = evaluate(lst)
    while True:
        moved = False
        for p in range(n):
            for q in range(n):
                if p == q:
                    continue
                cand = list(lst)
                job = cand.pop(p)
                cand.insert(q, job)
                if not topo_ok(cand):
                    continue
                M = evaluate(cand)
                if M < best:
                    lst, best = cand, M
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break
    return best


def build(instance):
    dur = instance["durations_data"]
    need = instance["resource_needs_data"]
    cap = instance["resource_capacities_data"]
    succ = instance["successors_link_data"]
    n = len(dur)
    R = len(cap)

    preds = [[] for _ in range(n)]
    succs = [[] for _ in range(n)]
    for a, b in succ:
        preds[b].append(a)
        succs[a].append(b)

    # Longest chain of durations from each job to the end, the job itself included.
    tail = list(dur)
    for _ in range(n):
        for a, b in succ:
            tail[a] = max(tail[a], dur[a] + tail[b])
    # Earliest start from the precedence constraints.
    head = [0] * n
    for _ in range(n):
        for a, b in succ:
            head[b] = max(head[b], head[a] + dur[a])

    # Lower bound on the makespan: the longest precedence chain, and for each resource
    # the total work it must carry divided by its capacity, rounded up.
    lb_makespan = max(head[i] + tail[i] for i in range(n))
    for k in range(R):
        work = sum(need[i][k] * dur[i] for i in range(n))
        lb_makespan = max(lb_makespan, -(-work // cap[k]))

    # Upper bound on the makespan: a feasible schedule found by a fixed local search (no
    # random sampling). Its makespan is only used as the planning horizon.
    horizon = sum(dur) + 1
    ub_makespan = min(sum(dur), _heuristic_makespan(dur, need, cap, preds, succs, succ,
                                                    horizon))
    ub_makespan = max(ub_makespan, lb_makespan)

    # Every job starts in its window: no earlier than its head, and early enough that
    # the longest chain after it still ends by the upper bound.
    E = head
    L = [ub_makespan - tail[i] for i in range(n)]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    makespan = model.add_var("makespan", lb=lb_makespan, ub=ub_makespan, var_type=mip.INTEGER)
    start = [model.add_var("start_%d" % i, lb=E[i], ub=L[i], var_type=mip.INTEGER)
             for i in range(n)]

    # y[i][t] = 1 when job i has started by time t (a step function in t). It is fixed
    # to 0 before the window and to 1 from the latest start on.
    Y = {}
    for i in range(n):
        Y[i] = {t: model.add_var("y_%d_%d" % (i, t), var_type=mip.BINARY)
                for t in range(E[i], L[i])}

    def yv(i, t):
        if t < E[i]:
            return 0
        if t >= L[i]:
            return 1
        return Y[i][t]

    for i in range(n):
        for t in range(E[i], L[i] - 1):
            model.add_constr(Y[i][t] <= Y[i][t + 1])
        # The start time is the latest start minus the number of steps taken before it.
        model.add_constr(start[i] + mip.xsum(Y[i].values()) == L[i])

    # The jobs have precedence constraints, meaning certain jobs must be completed before
    # others can start. Written per time t: if job b has started by t, then job a
    # has started by t minus its duration.
    for a, b in succ:
        d = dur[a]
        for t in range(E[b], L[b]):
            ya = yv(a, t - d)
            if isinstance(ya, int):
                if ya == 0:
                    model.add_constr(Y[b][t] <= 0)
            else:
                model.add_constr(Y[b][t] <= ya)
        ya = yv(a, L[b] - d)
        if not isinstance(ya, int):
            model.add_constr(ya >= 1)

    # The makespan is at least the completion time of every job.
    for i in range(n):
        model.add_constr(makespan >= start[i] + dur[i])

    # Each job runs for its duration without interruption, and at any time a job is active
    # from its start up to its completion: it is active at time tau when
    # y[tau] - y[tau - duration] = 1.
    def active(i, tau):
        d = dur[i]
        terms = []
        const = 0
        pos = yv(i, tau)
        neg = yv(i, tau - d)
        if isinstance(pos, int):
            const += pos
        else:
            terms.append((1, pos))
        if isinstance(neg, int):
            const -= neg
        else:
            terms.append((-1, neg))
        return terms, const

    # Two jobs cannot run at the same time when they are ordered by the precedence
    # constraints, or when together they need more of some resource than its capacity.
    # Such pairs form a conflict graph; every maximal clique of it is a set of jobs of
    # which at most one may be active at any time.
    reach = [[False] * n for _ in range(n)]
    for a, b in succ:
        reach[a][b] = True
    for m_ in range(n):
        for i in range(n):
            if reach[i][m_]:
                for j in range(n):
                    if reach[m_][j]:
                        reach[i][j] = True
    conf = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j or dur[i] == 0 or dur[j] == 0:
                continue
            if reach[i][j] or reach[j][i] or any(need[i][k] + need[j][k] > cap[k]
                                                  for k in range(R)):
                conf[i].add(j)

    cliques = []

    def bron_kerbosch(clique, cand, excl):
        if not cand and not excl:
            if len(clique) >= 2:
                cliques.append(sorted(clique))
            return
        for v in sorted(cand):
            bron_kerbosch(clique | {v}, cand & conf[v], excl & conf[v])
            cand = cand - {v}
            excl = excl | {v}

    bron_kerbosch(set(), {i for i in range(n) if conf[i]}, set())

    for C in cliques:
        for tau in range(ub_makespan):
            terms = []
            const = 0
            for i in C:
                t_i, c_i = active(i, tau)
                terms.extend(t_i)
                const += c_i
            if not terms:
                continue
            # Skip rows that cannot be violated.
            if sum(c for c, _ in terms if c > 0) + const <= 1:
                continue
            model.add_constr(mip.xsum(c * v for c, v in terms) <= 1 - const)

    # Each resource has a limited capacity that must not be exceeded at any time.
    # A job started at s is active during the times s .. s + duration - 1.
    for k in range(R):
        if sum(need[i][k] for i in range(n)) <= cap[k]:
            continue
        for tau in range(ub_makespan):
            terms = []
            const = 0
            for i in range(n):
                d = dur[i]
                r = need[i][k]
                if d == 0 or r == 0:
                    continue
                t_i, c_i = active(i, tau)
                terms.extend((r * c, v) for c, v in t_i)
                const += r * c_i
            if not terms:
                continue
            # Skip rows that cannot be violated.
            if sum(c for c, _ in terms if c > 0) + const <= cap[k]:
                continue
            model.add_constr(mip.xsum(c * v for c, v in terms) <= cap[k] - const)

    model.objective = makespan
    return model, {"start_time": start}
