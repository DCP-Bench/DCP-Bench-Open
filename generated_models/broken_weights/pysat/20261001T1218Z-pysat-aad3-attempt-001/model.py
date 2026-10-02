# Broken weights: a measuring weight of m pounds broke into n pieces of whole-pound
# weights. Find the weights of the pieces so that, on a balance scale where pieces go
# on either side, every whole weight from 1 to m can be weighed.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    m = instance["m"]  # total weight of the pieces
    n = instance["n"]  # number of pieces

    pool = IDPool()
    # weights[j] = the weight of piece j. Every piece weighs at least 1 and the pieces add
    # up to m, so a piece weighs at most m - (n - 1).
    top = m - (n - 1)
    weights = [Integer(f"weight{j}", 1, top, vpool=pool) for j in range(n)]
    engine = IntegerEngine(vars=weights, vpool=pool)
    cnf = engine.clausify()

    # A product weight * (-1, 0 or 1) is not a linear term, so each weight is also kept
    # as a binary number: bit[j][b] is bit b of the weight of piece j, tied to the
    # one-hot value literals of weights[j] (value v sets exactly the bits of v).
    n_bits = top.bit_length()
    bit = [[pool.id(("bit", j, b)) for b in range(n_bits)] for j in range(n)]
    for j in range(n):
        for v in range(1, top + 1):
            for b in range(n_bits):
                cnf.append([-weights[j].equals(v), bit[j][b] if (v >> b) & 1 else -bit[j][b]])

    # the pieces add up to the total weight
    cnf.extend(PBEnc.equals(lits=[bit[j][b] for j in range(n) for b in range(n_bits)],
                            weights=[1 << b for j in range(n) for b in range(n_bits)],
                            bound=m, vpool=pool).clauses)

    # Every weight 1..m can be weighed. To weigh target, each piece goes on the side of the
    # object (sign -1), on the other side (sign +1), or stays off the scale (sign 0), and
    # the signed pieces add up to target. plus/minus say which sign piece j gets.
    for target in range(1, m + 1):
        lits, coefficients = [], []
        for j in range(n):
            plus = pool.id(("plus", target, j))
            minus = pool.id(("minus", target, j))
            cnf.append([-plus, -minus])
            for b in range(n_bits):
                # `both` is true exactly when piece j has this sign and bit b of its weight is set
                for sign_lit, sign in ((plus, 1), (minus, -1)):
                    both = pool.id(("signed", target, j, b, sign))
                    cnf.append([-both, sign_lit])
                    cnf.append([-both, bit[j][b]])
                    cnf.append([both, -sign_lit, -bit[j][b]])
                    lits.append(both)
                    coefficients.append(sign * (1 << b))
        cnf.extend(PBEnc.equals(lits=lits, weights=coefficients, bound=target,
                                vpool=pool).clauses)

    return cnf, {"weights": weights}
