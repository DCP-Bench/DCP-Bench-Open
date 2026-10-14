# Hardy's 1729 square: find four different numbers a, b, c, d between 1 and 100 such that the
# sum of the squares of the first two equals the sum of the squares of the other two.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    range_min, range_max = 1, 100  # the numbers lie between 1 and 100 (given by the problem)

    pool = IDPool()
    numbers = [Integer(name, range_min, range_max, vpool=pool) for name in "abcd"]
    a, b, c, d = numbers
    engine = IntegerEngine(vars=numbers, vpool=pool)

    # the four numbers are all different
    engine.add_alldifferent(numbers)

    cnf = engine.clausify()

    # a^2 + b^2 == c^2 + d^2. PySAT cannot multiply two variables, so the squares are tabulated:
    # sum_is[s] stands for "the common sum of squares is s". Every pair of values of (a, b) and of
    # (c, d) forces the literal of its own sum, and at most one sum literal may hold, so both
    # pairs have to give the same sum.
    sum_is = {}
    for first, second in ((a, b), (c, d)):
        for u in range(range_min, range_max + 1):
            for v in range(range_min, range_max + 1):
                s = u * u + v * v
                if s not in sum_is:
                    sum_is[s] = pool.id(("sum", s))
                cnf.append([-first.equals(u), -second.equals(v), sum_is[s]])
    cnf.extend(CardEnc.atmost(lits=list(sum_is.values()), bound=1, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    return cnf, {"a": a, "b": b, "c": c, "d": d}
