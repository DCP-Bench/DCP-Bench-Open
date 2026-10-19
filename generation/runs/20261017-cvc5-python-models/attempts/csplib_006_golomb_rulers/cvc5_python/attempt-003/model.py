# Golomb ruler (csplib 006): m integers 0 = a_1 < a_2 < ... < a_m such that the
# m(m-1)/2 differences a_j - a_i (i < j) are all distinct. Minimise the length a_m.
# Outputs: marks = [a_1, ..., a_m] and length = a_m.
#
# Encoding: a Boolean occupancy on[p] for positions p in 0..U; a sequential counter
# ge[p][k] ("at least k marks in positions 0..p") that fixes exactly m marks; the marks
# are read off the counter; distinct differences as at-most-one over the pair literals
# of each distance d. U is the length of a greedy first-fit ruler computed from m alone.
# That bound is deterministic and derived from the instance size; it is extra work done
# outside the solver, and any ruler length is a valid upper bound on the optimum.
import cvc5.pythonic as cz


def first_fit_length(m):
    # Greedy first-fit Golomb ruler with m marks: its length bounds the optimum from above.
    marks = [0]
    used = set()
    x = 0
    while len(marks) < m:
        x += 1
        diffs = [x - a for a in marks]
        if len(set(diffs)) == len(diffs) and used.isdisjoint(diffs):
            marks.append(x)
            used.update(diffs)
    return marks[-1]


def at_most_one(lits, tag):
    # Sequential (ladder) at-most-one: s[i] is implied true when some literal in lits[0..i] is true.
    m = len(lits)
    if m < 2:
        return []
    s = [cz.Bool(f"{tag}_s{i}") for i in range(m - 1)]
    cons = [cz.Or(cz.Not(lits[0]), s[0]), cz.Or(cz.Not(lits[m - 1]), cz.Not(s[m - 2]))]
    for i in range(1, m - 1):
        cons.append(cz.Or(cz.Not(lits[i]), s[i]))
        cons.append(cz.Or(cz.Not(s[i - 1]), s[i]))
        cons.append(cz.Or(cz.Not(lits[i]), cz.Not(s[i - 1])))
    return cons


def build(instance):
    m = instance["size"]
    U = first_fit_length(m)
    cons = []

    # Occupancy: a mark at position p. The ruler starts with a mark at 0.
    on = [cz.Bool(f"on_{p}") for p in range(U + 1)]
    cons.append(on[0])

    # Exactly m marks in positions 0..U. ge[p][k] means at least k marks lie in 0..p (k = 1..m+1).
    K = m + 1
    ge = [[None] * (K + 1) for _ in range(U + 1)]
    for p in range(U + 1):
        for k in range(1, K + 1):
            ge[p][k] = cz.Bool(f"ge_{p}_{k}")
    for p in range(U + 1):
        for k in range(1, K + 1):
            if p == 0:
                if k == 1:
                    cons.append(ge[0][1] == on[0])
                else:
                    cons.append(cz.Not(ge[0][k]))
            elif k == 1:
                cons.append(ge[p][1] == cz.Or(ge[p - 1][1], on[p]))
            else:
                cons.append(ge[p][k] == cz.Or(ge[p - 1][k], cz.And(on[p], ge[p - 1][k - 1])))
    cons.append(ge[U][m])
    cons.append(cz.Not(ge[U][m + 1]))

    # The differences are all distinct: for each distance d, at most one pair of marks
    # (p, p + d) lies in the ruler. pair[p][d] is true exactly when both ends are marked.
    for d in range(1, U + 1):
        pairs = []
        for p in range(U - d + 1):
            x = cz.Bool(f"pair_{p}_{d}")
            cons.append(x == cz.And(on[p], on[p + d]))
            pairs.append(x)
        cons += at_most_one(pairs, f"amo_{d}")

    # The marks: mark k (0-based) is the first position where the counter reaches k + 1.
    marks = [cz.Int(f"mark_{k}") for k in range(m)]
    for k in range(m):
        cons.append(marks[k] >= 0)
        cons.append(marks[k] <= U)
        for p in range(U):
            cons.append((marks[k] <= p) == ge[p][k + 1])
    cons.append(marks[0] == 0)

    length = marks[m - 1]
    s = cz.SolverFor("QF_LIA")
    s.add(*cons)
    return s, {"length": length, "marks": marks}, ("minimize", length)
