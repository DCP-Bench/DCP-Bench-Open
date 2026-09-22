# Order thirteen arrivals so the room is never more than 7 women to 3 men.
# The head counts are the puzzle, so the instance carries no fields.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    total_people = 13
    num_males = 4

    pool = IDPool()
    # true is a woman, false a man
    sequence = [pool.id(("p", i)) for i in range(total_people)]
    cnf = CNF()
    cnf.extend(CardEnc.equals(lits=sequence, bound=total_people - num_males,
                              vpool=pool, encoding=EncType.seqcounter).clauses)

    # After i arrivals: 3 * women <= 7 * men, with men = i - women, so
    # 10 * women <= 7 * i.
    for i in range(1, total_people):
        cnf.extend(PBEnc.leq(lits=sequence[:i], weights=[10] * i, bound=7 * i,
                             vpool=pool).clauses)
    return cnf, {"sequence": sequence}
