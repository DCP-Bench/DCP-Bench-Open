# Golomb rulers (CSPLib 6): place `size` marks at integer positions starting
# at 0 so that all differences between pairs of marks are distinct, with the
# last mark (the ruler's length) as small as possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    size = instance["size"]
    # Marks lie in 0 .. size * size, the domain the reference declares.
    top = size * size

    pool = IDPool()
    # on[p] is true when a mark lies at position p. Stating the ruler over
    # positions turns "the differences are distinct" into "no two pairs of
    # marks lie the same distance apart", which needs no arithmetic.
    on = [pool.id(("on", p)) for p in range(top + 1)]
    # marks[k] is the position of the (k+1)-th mark from the left.
    marks = [Integer(f"marks{k}", 0, top, vpool=pool) for k in range(size)]

    formula = WCNF()
    formula.extend(IntegerEngine(vars=marks, vpool=pool).clausify().clauses)

    # atleast[p][k] is true when at least k marks lie at positions 0 .. p
    # (k = 0 .. size + 1), defined both ways so it is exactly that count.
    def atleast(p, k):
        return pool.id(("atleast", p, k))

    for p in range(top + 1):
        formula.append([atleast(p, 0)])
        for k in range(1, size + 2):
            here = atleast(p, k)
            if p == 0:
                # only position 0 counts: at least 1 iff it holds a mark
                if k == 1:
                    formula.append([-here, on[0]])
                    formula.append([here, -on[0]])
                else:
                    formula.append([-here])
                continue
            before, before_less = atleast(p - 1, k), atleast(p - 1, k - 1)
            # at least k up to p iff at least k up to p - 1, or k - 1 up to
            # p - 1 and a mark at p
            formula.append([-before, here])
            formula.append([-before_less, -on[p], here])
            formula.append([-here, before, before_less])
            formula.append([-here, before, on[p]])

    # The ruler has exactly `size` marks.
    formula.append([atleast(top, size)])
    formula.append([-atleast(top, size + 1)])

    # The first mark is at 0.
    formula.append([on[0]])

    # The marks are increasing: marks[k] is the position p that holds a mark
    # with exactly k marks before it.
    for k in range(size):
        for p in range(top + 1):
            eq = marks[k].equals(p)
            if p == 0:
                cond = [on[0]] if k == 0 else None
            else:
                cond = [on[p], atleast(p - 1, k), -atleast(p - 1, k + 1)]
            if cond is None:
                formula.append([-eq])
                continue
            for lit in cond:
                formula.append([-eq, lit])
            formula.append([-lit for lit in cond] + [eq])

    # All differences between marks are distinct: for each distance d, at most
    # one pair of positions d apart both hold a mark. pair[(p, d)] stands for
    # "marks at p and p + d" and is implied by the two marks.
    for d in range(1, top + 1):
        pairs = []
        for p in range(0, top + 1 - d):
            pair = pool.id(("pair", p, d))
            formula.append([-on[p], -on[p + d], pair])
            pairs.append(pair)
        if len(pairs) > 1:
            formula.extend(CardEnc.atmost(lits=pairs, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # Minimise the length, the position of the last mark: for every position
    # p >= 1 that the ruler reaches, that is whenever not all marks lie in
    # 0 .. p - 1, pay 1. The total paid is the length.
    for p in range(1, top + 1):
        formula.append([atleast(p - 1, size)], weight=1)

    return formula, {"marks": marks, "length": marks[-1]}
