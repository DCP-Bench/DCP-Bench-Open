# Assign each item to a bin without exceeding the bin capacity.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    pool = IDPool()
    bins = [Integer(f"bin{j}", 0, num_bins - 1, vpool=pool) for j in range(n)]
    engine = IntegerEngine(vars=bins, vpool=pool)
    cnf = engine.clausify()
    for b in range(num_bins):
        here = [bins[j].equals(b) for j in range(n)]
        cnf.extend(PBEnc.leq(lits=here, weights=list(weights), bound=capacity,
                             vpool=pool).clauses)
    return cnf, {"bins": bins}
