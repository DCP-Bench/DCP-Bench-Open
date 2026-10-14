# Golomb rulers (CSPLib 6): place `size` marks at integer positions 0 = a_1 < a_2 <
# ... < a_m so that all differences a_j - a_i between two marks are distinct, and make
# the ruler as short as possible (its length is the position of the last mark).
#
# The model is purely Boolean, so Z3 can minimise the length as MaxSAT over its SAT
# core: each mark is order-encoded (ge[i][p] says mark i lies at position p or
# beyond), and on[p] says some mark lies at position p. Over positions, "all
# differences are distinct" becomes "no two pairs of marked positions lie the same
# distance apart", a set of cardinality constraints with no arithmetic. With integer
# marks and Distinct over the differences, Z3 does not prove the optimum for 8, 9 or
# 10 marks within 180 s.
import z3


def build(instance):
    size = instance["size"]  # number of marks

    # ---- Bounds computed before Z3 runs (plain Python) ----

    class OutOfBudget(Exception):
        pass

    def ruler_within(marks_wanted, limit, least, budget=None):
        """A Golomb ruler with marks_wanted marks and length <= limit, or None. least[k]
        is a lower bound on the length of any k-mark ruler, used to prune. With a
        budget (of candidate positions tried), None also means it ran out."""
        marks, diffs, tried = [0], set(), [0]

        def extend():
            if len(marks) == marks_wanted:
                return True
            rest = marks_wanted - len(marks) - 1  # marks still to place after this one
            # the marks so far plus this one form a ruler of len(marks) + 1 marks, and
            # this one plus the rest form a ruler of rest + 1 marks
            first = max(marks[-1] + 1, least[len(marks) + 1])
            for p in range(first, limit - least[rest + 1] + 1):
                tried[0] += 1
                if budget is not None and tried[0] > budget:
                    raise OutOfBudget
                new = [p - m for m in marks]
                if any(d in diffs for d in new):
                    continue
                diffs.update(new)
                marks.append(p)
                if extend():
                    return True
                marks.pop()
                diffs.difference_update(new)
            return False

        try:
            return list(marks) if extend() else None
        except OutOfBudget:
            return None

    # least[k] is a lower bound on the length of any Golomb ruler with k marks:
    #  - its k(k-1)/2 differences are distinct positive integers, so >= k(k-1)/2;
    #  - removing its last mark leaves a ruler of k - 1 marks, so >= least[k-1] + 1;
    #  - its first a marks and its last b marks (a + b = k + 1, sharing one mark) are
    #    rulers whose lengths add up to its length, so >= least[a] + least[b].
    # For small k (up to 7 marks, and never the instance's own size) the shortest
    # length is found exactly by exhaustive search.
    least = [0] * (size + 1)

    def derived(k):
        if k <= 1:
            return 0
        bound = max(k * (k - 1) // 2, least[k - 1] + 1)
        for a in range(2, k):
            bound = max(bound, least[a] + least[k + 1 - a])
        return bound

    exact_up_to = min(size - 1, 7)
    for k in range(1, size + 1):
        least[k] = derived(k)
        if k <= exact_up_to:
            while ruler_within(k, least[k], least) is None:
                least[k] += 1

    # Upper bound on the length: any ruler with `size` marks is at least as long as
    # the shortest one, so positions beyond the length of a known ruler are never
    # needed. The first-fit ruler (each mark at the first position that repeats no
    # difference) gives one; a depth-first search with a fixed budget of tried
    # positions then looks for shorter ones.
    def first_fit():
        marks, diffs = [0], set()
        while len(marks) < size:
            p = marks[-1] + 1
            while any(p - m in diffs for m in marks):
                p += 1
            diffs.update(p - m for m in marks)
            marks.append(p)
        return marks[-1]

    upper = first_fit()
    while upper > least[size]:
        found = ruler_within(size, upper - 1, least, 100000)
        if found is None:
            break
        upper = found[-1]
    # never beyond the domain the problem itself states for the marks (0 .. size^2)
    top = min(upper, size * size)

    solver = z3.Solver()

    # ge[i][p] is true when mark i lies at position p or beyond (p = 1 .. top). Mark 0
    # is the first mark, at 0; no mark lies beyond top.
    ge = [None] + [[None] + [z3.Bool(f"ge_{i}_{p}") for p in range(1, top + 1)]
                   for i in range(1, size)]

    def at_least(i, p):
        if p <= 0:
            return z3.BoolVal(True)
        if p > top or i == 0:
            return z3.BoolVal(False)
        return ge[i][p]

    for i in range(1, size):
        for p in range(1, top):
            solver.add(z3.Implies(ge[i][p + 1], ge[i][p]))

    # The marks are increasing, and any marks i < j enclose a ruler of j - i + 1 marks,
    # so mark j lies at least least[j - i + 1] beyond mark i (least[2] = 1 is the
    # strict increase). Stated per position: mark i at p or beyond puts mark j at
    # p + least[j - i + 1] or beyond.
    for i in range(size):
        for j in range(i + 1, size):
            gap = least[j - i + 1]
            for p in range(0, top + 1):
                solver.add(z3.Implies(at_least(i, p), at_least(j, p + gap)))

    # on[p] is true when a mark lies at position p: mark i is at p when it is at p or
    # beyond but not at p + 1 or beyond. The ruler has exactly `size` marks, so on[]
    # holds exactly the marked positions.
    on = [z3.Bool(f"on_{p}") for p in range(top + 1)]
    for i in range(size):
        for p in range(top + 1):
            solver.add(z3.Implies(z3.And(at_least(i, p), z3.Not(at_least(i, p + 1))), on[p]))
    solver.add(z3.PbEq([(b, 1) for b in on], size))

    # All differences between two marks are distinct: for each distance d, at most one
    # pair of marked positions (p, p + d) exists. pair is forced true by its two marks.
    for d in range(1, top + 1):
        pairs = []
        for p in range(top + 1 - d):
            pair = z3.Bool(f"pair_{p}_{d}")
            solver.add(z3.Implies(z3.And(on[p], on[p + d]), pair))
            pairs.append(pair)
        if len(pairs) > 1:
            solver.add(z3.AtMost(*pairs, 1))

    # Implied (stated for the solver): k marks span at least least[k], so any least[k]
    # consecutive positions hold at most k - 1 marks.
    for k in range(3, size + 1):
        width = least[k]
        for p in range(top + 2 - width):
            solver.add(z3.AtMost(*on[p:p + width], k - 1))

    # marks[i] is the position of mark i, read off its order encoding as a chain
    # "0 if not at 1 or beyond, else 1 if not at 2 or beyond, ...". Comparing such a
    # chain with a number simplifies to a Boolean formula, so excluding a found
    # solution (when several are asked for) needs no arithmetic.
    def position(i):
        value = z3.IntVal(top)
        for p in range(top, 0, -1):
            value = z3.If(z3.Not(at_least(i, p)), p - 1, value)
        return value

    marks = [position(i) for i in range(size)]
    length = marks[size - 1]

    # Minimise the length of the ruler, the position of the last mark. The same
    # length, written as the number of positions p >= 1 the last mark lies at or
    # beyond, is a sum of Boolean terms, which Z3 minimises as MaxSAT.
    objective = z3.Sum([z3.IntVal(0)] + [z3.If(at_least(size - 1, p), 1, 0)
                                         for p in range(1, top + 1)])
    return solver, {"marks": marks, "length": length}, ("minimize", objective)
