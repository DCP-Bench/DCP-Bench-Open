# Pick exactly m of the given integers so that they sum to zero.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    nums = instance["nums"]
    wanted = instance["m"]

    pool = IDPool()
    indices = [pool.id(("i", k)) for k in range(len(nums))]
    cnf = CNF()
    # PBEnc takes the negative numbers as weights directly.
    cnf.extend(PBEnc.equals(lits=indices, weights=list(nums), bound=0,
                            vpool=pool).clauses)
    cnf.extend(CardEnc.equals(lits=indices, bound=wanted, vpool=pool,
                              encoding=EncType.seqcounter).clauses)
    return cnf, {"indices": indices}
