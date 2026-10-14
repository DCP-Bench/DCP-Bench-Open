# Bus driver scheduling (CSPLib 022): select shifts so that every piece of
# work is covered by exactly one selected shift, using as few shifts as
# possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def build(instance):
    num_work = instance["num_work"]
    num_shifts = instance["num_shifts"]
    shifts = instance["shifts"]  # the pieces of work each shift covers

    pool = IDPool()
    formula = WCNF()

    # x[i] is true when shift i is selected.
    x = [pool.id(("x", i)) for i in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift.
    for t in range(num_work):
        covering = [x[i] for i in range(num_shifts) if t in shifts[i]]
        if not covering:
            # No shift covers this piece of work: the instance is infeasible.
            formula.append([x[0]])
            formula.append([-x[0]])
            continue
        formula.extend(CardEnc.equals(lits=covering, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Minimise the number of shifts used: every selected shift pays 1.
    for i in range(num_shifts):
        formula.append([-x[i]], weight=1)

    return formula, {"x": x}
