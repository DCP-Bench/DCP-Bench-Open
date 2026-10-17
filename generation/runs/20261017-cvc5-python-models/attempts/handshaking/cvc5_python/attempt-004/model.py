# Handshaking problem (Halmos): Hilary and Jocelyn are married and invite
# num_couples couples. Everyone shakes hands, but nobody shakes hands with
# themselves or with their spouse. Jocelyn asks each person how many hands they
# shook, and all the answers are different. Output: the number of hands Hilary shook.
#
# Pure Boolean encoding: the hand counts are unary (sequential counters over the
# handshake Booleans), so no integer arithmetic is needed for the distinctness.
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_couples"]
    # Person 0 is Hilary, person 1 is Jocelyn, then the invited couples as (2k, 2k+1).
    people = 2 * n + 2
    m = people - 1  # each person can shake hands with at most this many others
    top = 2 * n     # an answer is a number of hands among the 2n+1 others

    constraints = []
    fresh = [0]

    def new_bool():
        fresh[0] += 1
        return cz.Bool(f"aux_{fresh[0]}")

    def NOT(a):
        if isinstance(a, bool):
            return not a
        return cz.Not(a)

    def OR(a, b):
        if a is True or b is True:
            return True
        if a is False:
            return b
        if b is False:
            return a
        return cz.Or(a, b)

    def AND(a, b):
        if a is False or b is False:
            return False
        if a is True:
            return b
        if b is True:
            return a
        return cz.And(a, b)

    def define(expr):
        # A fresh Boolean equal to expr, so the counters stay small terms.
        if isinstance(expr, bool):
            return expr
        v = new_bool()
        constraints.append(v == expr)
        return v

    def ite(c, a, b):
        if c is True:
            return a
        if c is False:
            return b
        return cz.If(c, a, b)

    # One Boolean per unordered pair: True when the two shake hands.
    # Nobody shakes hands with his or her spouse, so that pair is fixed to False.
    h = {}
    for i in range(people):
        for j in range(i + 1, people):
            h[(i, j)] = False if j == (i ^ 1) else cz.Bool(f"h_{i}_{j}")

    def hand(i, j):
        if i == j:
            return False  # nobody shakes hands with him or herself
        return h[(i, j)] if i < j else h[(j, i)]

    # The number of hands each person has shaken, in unary form: at_least[i][k]
    # means person i has shaken at least k hands. Built as a sequential counter
    # over that person's handshakes, each step reified in both directions.
    at_least = {}
    for i in range(people):
        others = [k for k in range(people) if k != i]
        prev = [True] + [False] * m
        for x_idx in range(m):
            x = hand(i, others[x_idx])
            cur = [True]
            for k in range(1, m + 1):
                cur.append(define(OR(prev[k], AND(x, prev[k - 1]))))
            prev = cur
        at_least[i] = prev  # length m+1

    # The exact count of person i is v when at_least[i][v] holds and at_least[i][v+1] does not.
    def exactly(i, v):
        nxt = at_least[i][v + 1] if v + 1 <= m else False
        return define(AND(at_least[i][v], NOT(nxt)))

    # All the answers are different. Jocelyn asks the others, so her own count is left out.
    # With 2n+1 answers in 0..2n, every value is then taken by exactly one answerer.
    answerers = [i for i in range(people) if i != 1]
    count_is = {i: [exactly(i, v) for v in range(top + 1)] for i in answerers}
    for v in range(top + 1):
        # At least one answerer has the value v.
        constraints.append(cz.Or([count_is[i][v] for i in answerers]))
        # At most one answerer has the value v.
        for a in range(len(answerers)):
            for b in range(a + 1, len(answerers)):
                ia, ib = answerers[a], answerers[b]
                constraints.append(NOT(AND(count_is[ia][v], count_is[ib][v])))

    # The answers are the values 0..2n, one each, so their total is 0+1+...+2n.
    # The answers are different, so the total is fixed; this is implied by the constraint above.
    total = cz.Sum([ite(count_is[i][v], v, 0) for i in answerers for v in range(top + 1)])
    constraints.append(total == n * (2 * n + 1))

    hil = cz.Sum([ite(count_is[0][v], v, 0) for v in range(top + 1)])
    return constraints, {"hil": hil}
