# Knock over the dummies whose numbers add up to exactly the target.
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    values = instance["values"]
    target = instance["target_sum"]

    pool = IDPool()
    dummies = [pool.id(("d", i)) for i in range(len(values))]
    cnf = CNF()
    cnf.extend(PBEnc.equals(lits=dummies, weights=list(values), bound=target,
                            vpool=pool).clauses)
    return cnf, {"dummies": dummies}
