# Hadamard matrix (Legendre pairs): for an odd l with m = (l - 1) / 2, find two
# sequences a and b of length l with entries +1 or -1, each summing to 1, whose
# periodic autocorrelations satisfy PAF(a, s) + PAF(b, s) = -2 for s = 1..m.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    l = instance["l"]  # length of the sequences (odd)
    half = (l - 1) // 2

    pool = IDPool()
    cnf = CNF()

    def sequence(name):
        """plus[i] is true when entry i is +1; values[i] is the entry itself, -1 or +1."""
        plus = [pool.id((name, "plus", i)) for i in range(l)]
        values = [Integer(f"{name}_{i}", -1, 1, vpool=pool) for i in range(l)]
        engine = IntegerEngine(vars=values, vpool=pool)
        cnf.extend(engine.clausify().clauses)
        for i in range(l):
            cnf.append([-plus[i], values[i].equals(1)])
            cnf.append([plus[i], values[i].equals(-1)])
        # the entries sum to 1: (l + 1) / 2 of them are +1
        cnf.extend(CardEnc.equals(lits=plus, bound=(l + 1) // 2, vpool=pool, encoding=EncType.seqcounter).clauses)
        return plus, values

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    def agreements(name, plus, s):
        """Literals that say whether entries i and i + s (mod l) are equal."""
        agree = []
        for i in range(l):
            p, q = plus[i], plus[(i + s) % l]
            same = pool.id((name, "same", s, i))
            cnf.append([-same, -p, q])
            cnf.append([-same, p, -q])
            cnf.append([same, p, q])
            cnf.append([same, -p, -q])
            agree.append(same)
        return agree

    # PAF(a, s) + PAF(b, s) = -2. Each PAF is 2 * (equal pairs) - l, so the
    # condition says that the equal pairs of a and b together number l - 1.
    for s in range(1, half + 1):
        same = agreements("a", plus_a, s) + agreements("b", plus_b, s)
        cnf.extend(CardEnc.equals(lits=same, bound=l - 1, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"a": a, "b": b}
