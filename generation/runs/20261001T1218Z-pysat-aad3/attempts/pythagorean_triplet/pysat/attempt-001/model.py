# Pythagorean triplet: find natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    total = 1000          # a + b + c has to equal this (given by the problem)
    low, high = 1, 500    # a, b and c are natural numbers; none can exceed half the total

    pool = IDPool()
    a = Integer("a", low, high, vpool=pool)
    b = Integer("b", low, high, vpool=pool)
    c = Integer("c", low, high, vpool=pool)
    engine = IntegerEngine(vars=[a, b, c], vpool=pool)
    cnf = engine.clausify()

    # square_sum_is[s] stands for "a^2 + b^2 and c^2 are both s". PySAT cannot multiply two
    # variables, so the squares are tabulated: every pair of values of (a, b) forces the literal
    # of its own sum of squares, every value of c forces the literal of its own square, and at
    # most one such literal may hold, so a^2 + b^2 == c^2.
    square_sum_is = {}

    def literal_of(value):
        if value not in square_sum_is:
            square_sum_is[value] = pool.id(("square_sum", value))
        return square_sum_is[value]

    for u in range(low, high + 1):
        for v in range(low, high + 1):
            cnf.append([-a.equals(u), -b.equals(v), literal_of(u * u + v * v)])
            # a + b + c == total: once a and b are chosen, c is total - a - b (and it must be a
            # value c can take)
            w = total - u - v
            if low <= w <= high:
                cnf.append([-a.equals(u), -b.equals(v), c.equals(w)])
            else:
                cnf.append([-a.equals(u), -b.equals(v)])
    for w in range(low, high + 1):
        cnf.append([-c.equals(w), literal_of(w * w)])
    cnf.extend(CardEnc.atmost(lits=list(square_sum_is.values()), bound=1, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    return cnf, {"a": a, "b": b, "c": c}
