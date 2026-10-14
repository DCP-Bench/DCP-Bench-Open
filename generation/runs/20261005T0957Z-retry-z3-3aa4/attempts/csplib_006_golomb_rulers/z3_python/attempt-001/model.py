# Golomb rulers (CSPLib 6): place `size` marks at integer positions 0 = a_1 < a_2 <
# ... < a_m so that all differences a_j - a_i between two marks are distinct, and make
# the ruler as short as possible (its length is the position of the last mark).
#
# The model is stated over positions rather than mark values: on[p] says a mark lies
# at position p. "All differences are distinct" then becomes "no two pairs of marked
# positions lie the same distance apart", a set of cardinality constraints with no
# arithmetic, and the length is a sum of Boolean terms, so Z3 can minimise it as
# MaxSAT over its SAT core. An integer model with Distinct over the differences did
# not prove the optimum for 8, 9 or 10 marks in 180 s.
import z3


def build(instance):
    size = instance["size"]  # number of marks

    # ---- Upper bound on the length, computed from the instance before Z3 runs ----
    # Any Golomb ruler with `size` marks is at least as long as the shortest one, so
    # positions beyond the length of a known ruler are never needed. The first-fit
    # ruler (each mark at the first position that repeats no difference) gives one;
    # a depth-first search with a fixed budget of tried positions then looks for
    # shorter ones.
    def first_fit():
        marks, diffs = [0], set()
        while len(marks) < size:
            p = marks[-1] + 1
            while any(p - m in diffs for m in marks):
                p += 1
            diffs.update(p - m for m in marks)
            marks.append(p)
        return marks[-1]

    class OutOfBudget(Exception):
        pass

    def ruler_within(limit, budget):
        """A ruler with `size` marks and length <= limit, or None (also when the
        budget of candidate positions tried runs out)."""
        marks, diffs, nodes = [0], set(), [0]

        def extend():
            if len(marks) == size:
                return True
            rest = size - len(marks) - 1  # marks still to place after this one
            # the remaining marks form a ruler of rest + 1 marks starting here, whose
            # rest gaps are distinct positive integers, so it spans >= rest(rest+1)/2
            for p in range(marks[-1] + 1, limit - rest * (rest + 1) // 2 + 1):
                nodes[0] += 1  # one candidate position tried
                if nodes[0] > budget:
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

    upper = first_fit()
    while upper > 0:
        found = ruler_within(upper - 1, 100000)
        if found is None:
            break
        upper = found[-1]
    # never beyond the domain the problem itself states for the marks (0 .. size^2)
    top = min(upper, size * size)

    solver = z3.Solver()

    # on[p] is true when a mark lies at position p, p = 0 .. top.
    on = [z3.Bool(f"on_{p}") for p in range(top + 1)]

    # The first mark is at 0.
    solver.add(on[0])

    # The ruler has exactly `size` marks.
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

    # Implied (stated for the solver): k marks have k - 1 distinct positive gaps
    # between consecutive marks, so they span at least k(k-1)/2. Any k(k-1)/2
    # consecutive positions therefore hold at most k - 1 marks.
    for k in range(3, size + 1):
        width = k * (k - 1) // 2
        for p in range(top + 2 - width):
            solver.add(z3.AtMost(*on[p:p + width], k - 1))

    # fewer[p][k] is true when fewer than k marks lie at positions 0 .. p, defined
    # exactly by counting along the positions (k = 1 .. size).
    fewer = [[None] * (size + 1) for _ in range(top + 1)]
    for p in range(top + 1):
        for k in range(1, size + 1):
            fewer[p][k] = z3.Bool(f"fewer_{p}_{k}")
            if p == 0:
                # only position 0 counts: fewer than 1 iff no mark there, and always
                # fewer than 2 or more
                solver.add(fewer[0][k] == (z3.Not(on[0]) if k == 1 else z3.BoolVal(True)))
            else:
                # fewer than k up to p iff fewer than k up to p - 1, and either no mark
                # at p or fewer than k - 1 up to p - 1
                below = fewer[p - 1][k - 1] if k > 1 else z3.BoolVal(False)
                solver.add(fewer[p][k] == z3.And(fewer[p - 1][k], z3.Or(below, z3.Not(on[p]))))

    # marks[k] is the position of the (k+1)-th mark from the left: the number of
    # positions p >= 1 with at most k marks before p. These are increasing by
    # construction and marks[0] = 0.
    marks = [z3.Sum([z3.IntVal(0)] + [z3.If(fewer[p - 1][k + 1], 1, 0) for p in range(1, top + 1)])
             for k in range(size)]
    length = marks[size - 1]

    # Implied lower bound on the length: the size(size-1)/2 differences are distinct
    # positive integers no larger than the length, so the last mark is at
    # size(size-1)/2 or beyond.
    for p in range(min(size * (size - 1) // 2, top + 1)):
        solver.add(fewer[p][size])

    # Minimise the length of the ruler, the position of the last mark.
    return solver, {"marks": marks, "length": length}, ("minimize", length)
