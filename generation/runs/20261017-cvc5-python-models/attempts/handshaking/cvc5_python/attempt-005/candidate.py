# Handshaking problem: Hilary and Jocelyn are married and invite num_couples
# couples who are friends. When they arrive, they shake hands with each other.
# Nobody shakes hands with him or herself or with his or her spouse. Jocelyn asks
# how many hands each person has shaken, and all the answers are different.
# Output: the number of hands Hilary has shaken (hil).
#
# Encoding by rank. Jocelyn asks the 2n+1 people other than herself. Their answers
# are distinct values in 0..2n, so each value 0..2n is the answer of exactly one
# person. Rank r is the person who answers r. Jocelyn is an extra vertex J that
# shakes hands too (her handshakes count towards the answerers' totals). Handshakes
# are Booleans between ranks and between a rank and J. The spouses form a perfect
# matching on the 2n+2 people: Jocelyn's spouse is Hilary, and the other couples
# are pairs of ranks.
import cvc5.pythonic as cz


def build(instance):
    n = instance["num_couples"]
    top = 2 * n  # the answers are 0..2n
    ranks = list(range(top + 1))

    s = cz.SolverFor("QF_LIA")

    def exactly_one(lits):
        s.add(cz.Or(lits))
        for a in range(len(lits)):
            for b in range(a + 1, len(lits)):
                s.add(cz.Not(cz.And(lits[a], lits[b])))

    # Handshake between two ranks, one Boolean per unordered pair.
    shake = {}
    for r in ranks:
        for t in ranks:
            if r < t:
                shake[(r, t)] = cz.Bool(f"shake_{r}_{t}")

    def hand(r, t):
        return shake[(r, t)] if r < t else shake[(t, r)]

    # Handshake between rank r and Jocelyn.
    jh = [cz.Bool(f"jh_{r}") for r in ranks]

    # Spouse pairs between two ranks, and the rank that is Hilary (married to Jocelyn).
    spouse = {}
    for r in ranks:
        for t in ranks:
            if r < t:
                spouse[(r, t)] = cz.Bool(f"sp_{r}_{t}")

    def married(r, t):
        return spouse[(r, t)] if r < t else spouse[(t, r)]

    is_hilary = [cz.Bool(f"hil_{r}") for r in ranks]

    # Nobody shakes hands with him or herself: no self loops (only unordered pairs of
    # distinct ranks exist), and the rank-to-Jocelyn handshake is a separate Boolean.

    # Nobody shakes hands with his or her spouse.
    for (r, t), sp in spouse.items():
        s.add(cz.Implies(sp, cz.Not(shake[(r, t)])))
    for r in ranks:
        s.add(cz.Implies(is_hilary[r], cz.Not(jh[r])))

    # Each person has exactly one spouse: Jocelyn's spouse is Hilary, and every other
    # person is married to exactly one other person.
    exactly_one(is_hilary)
    for r in ranks:
        options = [married(r, t) for t in ranks if t != r] + [is_hilary[r]]
        exactly_one(options)

    # The person who answers r has shaken exactly r hands (with the others or with Jocelyn).
    for r in ranks:
        degree = [cz.If(hand(r, t), 1, 0) for t in ranks if t != r] + [cz.If(jh[r], 1, 0)]
        s.add(cz.Sum(degree) == r)

    hil = cz.Sum([cz.If(is_hilary[r], r, 0) for r in ranks])
    return s, {"hil": hil}
