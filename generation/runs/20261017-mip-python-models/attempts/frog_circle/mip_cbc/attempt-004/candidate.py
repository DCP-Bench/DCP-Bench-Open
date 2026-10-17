# Frog circle: cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then
# jumps to the card 1 place clockwise around the circle. From card k it jumps k places
# clockwise, forever. Find an arrangement x of the cards 1 to n (in clockwise order) that
# lets the frog jump on every card starting from card 1.
#
# Formulation: positions 0..n-1 hold the cards. The frog's walk is a path of arcs
# p -> (p + x[p]) mod n that starts at position 0 and visits every position once. The
# arc leaving p has length d = x[p] in 1..n-1. The n-1 path arcs carry distinct lengths,
# so they are exactly 1..n-1, and the last position of the path holds card n.
import mip


def build(instance):
    # n, the number of cards, comes from the instance
    n = instance["n"]
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # e[p, d] = 1 if the frog jumps from position p by d places (d in 1..n-1).
    # An arc into position 0 is left out: the walk starts there and never returns to it.
    e = {}
    for p in range(n):
        for d in range(1, n):
            if (p + d) % n != 0:
                e[p, d] = m.add_var(f"e_{p}_{d}", var_type=mip.BINARY)

    # x[p] = the card at position p
    x = [m.add_var(f"x_{p}", lb=1, ub=n, var_type=mip.INTEGER) for p in range(n)]

    # each position jumps at most once: the frog leaves it at most once
    for p in range(n):
        m.add_constr(mip.xsum(e[p, d] for d in range(1, n) if (p, d) in e) <= 1)

    # the frog lands on every position except the start, and each position once
    incoming = {q: [] for q in range(n)}
    outgoing = {q: [] for q in range(n)}
    for (p, d) in e:
        incoming[(p + d) % n].append((p, d))
        outgoing[p].append((p, d))
    for q in range(1, n):
        m.add_constr(mip.xsum(e[p, d] for (p, d) in incoming[q]) == 1)

    # the card at each position is its jump length: the arrangement uses the cards 1 to n
    # each exactly once, so each jump length 1..n-1 is used by exactly one arc
    for d in range(1, n):
        m.add_constr(mip.xsum(e[p, d] for p in range(n) if (p, d) in e) == 1)

    # from card k the frog jumps k places clockwise: a position with an outgoing arc of
    # length d holds card d; a position with no outgoing arc is the last one and holds card n
    for p in range(n):
        out_p = mip.xsum(e[p, d] for d in range(1, n) if (p, d) in e)
        m.add_constr(
            x[p] == mip.xsum(d * e[p, d] for d in range(1, n) if (p, d) in e) + n - n * out_p
        )

    # rotation convention: the frog starts on card 1, which is the first card of the
    # arrangement (a rotation of the circle gives the same frog walk)
    m.add_constr(x[0] == 1)

    # no cycle apart from the walk: a unit of flow leaves the start for every position the
    # walk reaches, so no arcs can form a loop that the walk from position 0 does not reach.
    # f[p, d] is the flow on the arc, and it can only be used when the arc is used
    f = {}
    for (p, d) in e:
        f[p, d] = m.add_var(f"f_{p}_{d}", lb=0, ub=n - 1, var_type=mip.CONTINUOUS)
        m.add_constr(f[p, d] <= (n - 1) * e[p, d])
    # every position other than the start consumes one unit of flow
    for q in range(1, n):
        m.add_constr(
            mip.xsum(f[p, d] for (p, d) in incoming[q])
            - mip.xsum(f[p, d] for (p, d) in outgoing[q]) == 1
        )

    # no objective: this is a satisfaction problem
    return m, {"x": x}
