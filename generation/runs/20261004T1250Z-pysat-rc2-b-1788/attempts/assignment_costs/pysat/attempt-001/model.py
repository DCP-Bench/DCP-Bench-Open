# Assignment with costs: give every task to exactly one person, each person
# taking at most one task, so that the total cost is minimal.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.pb import PBEnc


def build(instance):
    cost = instance["cost"]  # rows are tasks, columns are people
    rows = len(cost)
    cols = len(cost[0])

    pool = IDPool()
    # x[i][j] is true when task i is assigned to person j.
    x = [[pool.id(("x", i, j)) for j in range(cols)] for i in range(rows)]

    formula = WCNF()
    # Every task is assigned to exactly one person.
    for i in range(rows):
        formula.extend(CardEnc.equals(lits=x[i], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
    # Every person takes zero or one tasks.
    for j in range(cols):
        formula.extend(CardEnc.atmost(lits=[x[i][j] for i in range(rows)], bound=1,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    # The reference keeps the total cost within 0 .. sum of all costs. With
    # non-negative costs that always holds; it can only bind when some cost is
    # negative, so it is stated only then.
    lits = [x[i][j] for i in range(rows) for j in range(cols)]
    weights = [cost[i][j] for i in range(rows) for j in range(cols)]
    if any(w < 0 for w in weights):
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=0, vpool=pool).clauses)
        formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=sum(weights),
                                 vpool=pool).clauses)

    # Minimise the total cost: assigning task i to person j pays cost[i][j].
    # A negative cost is paid when the assignment is not made, which differs
    # from the cost by a constant.
    for lit, w in zip(lits, weights):
        if w > 0:
            formula.append([-lit], weight=w)
        elif w < 0:
            formula.append([lit], weight=-w)

    return formula, {"x": x}
