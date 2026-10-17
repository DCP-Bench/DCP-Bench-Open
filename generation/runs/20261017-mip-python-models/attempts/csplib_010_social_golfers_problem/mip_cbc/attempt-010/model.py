# Social golfers problem (csplib 010): golfers play once a week in groups of a fixed size.
# Find a schedule of play over the weeks such that no two golfers play in the same group
# on more than one occasion. Output assign[i][j]: the 0-based group of golfer i in week j.
import mip


def build(instance):
    s = instance["group_size"]
    n_groups = instance["n_groups"]
    weeks = instance["n_weeks"]
    n = s * n_groups

    m = mip.Model(solver_name="CBC")  # satisfaction problem: no objective is set

    # plays[g][w][k] = 1 when golfer g is in group k in week w
    plays = [
        [[m.add_var(f"p_{g}_{w}_{k}", var_type=mip.BINARY) for k in range(n_groups)]
         for w in range(weeks)]
        for g in range(n)
    ]

    # Each golfer plays in exactly one group each week.
    for g in range(n):
        for w in range(weeks):
            m += mip.xsum(plays[g][w][k] for k in range(n_groups)) == 1

    # Each group in each week has exactly group_size golfers.
    for w in range(weeks):
        for k in range(n_groups):
            m += mip.xsum(plays[g][w][k] for g in range(n)) == s

    # Pair indicator together[a, b, w] (shared by all groups): it is 1 when a and b share a group in week w.
    together = {}
    for a in range(n):
        for b in range(a + 1, n):
            for w in range(weeks):
                t = m.add_var(f"t_{a}_{b}_{w}", lb=0, ub=1, var_type=mip.CONTINUOUS)
                together[(a, b, w)] = t
                for k in range(n_groups):
                    m += t >= plays[a][w][k] + plays[b][w][k] - 1

    def tog(a, b, w):
        return together[(min(a, b), max(a, b), w)]

    # Golfers meet in the same group at most once over all weeks.
    for a in range(n):
        for b in range(a + 1, n):
            m += mip.xsum(together[(a, b, w)] for w in range(weeks)) <= 1

    # Each golfer plays with exactly group_size - 1 others each week.
    for g in range(n):
        for w in range(weeks):
            m += mip.xsum(tog(g, h, w) for h in range(n) if h != g) == s - 1

    # Output: group number of each golfer in each week, tied to the one-hot placement.
    assign = [[m.add_var(f"assign_{i}_{j}", lb=0, ub=n_groups - 1, var_type=mip.INTEGER)
               for j in range(weeks)] for i in range(n)]
    for i in range(n):
        for j in range(weeks):
            m += assign[i][j] == mip.xsum(k * plays[i][j][k] for k in range(n_groups))

    return m, {"assign": assign}
