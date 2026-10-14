# Kidney exchange: choose donations along the compatibility graph so that as
# many people as possible receive a kidney, where anyone who gives a kidney
# must receive one and nobody gives or receives more than one.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def build(instance):
    num_people = instance["num_people"]
    compatible = instance["compatible"]  # 1-based: compatible[i] lists whom i can donate to
    people = range(num_people)

    pool = IDPool()
    # transplants[i][j] is true when person i donates a kidney to person j.
    transplants = [[pool.id(("transplants", i, j)) for j in people] for i in people]

    formula = WCNF()
    for i in people:
        gives = transplants[i]
        receives = [transplants[k][i] for k in people]
        # Person i donates to at most one person and receives from at most one.
        formula.extend(CardEnc.atmost(lits=gives, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        formula.extend(CardEnc.atmost(lits=receives, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        # Anyone who gives a kidney must receive one.
        for j in people:
            formula.append([-transplants[i][j]] + receives)
        # i can only donate to the people listed as compatible with i.
        for j in people:
            if j + 1 not in compatible[i]:
                formula.append([-transplants[i][j]])

    # Maximise the number of transplants: every possible donation not made
    # pays 1, so RC2 minimises the shortfall from the number of compatible
    # pairs.
    for i in people:
        for j in people:
            if j + 1 in compatible[i]:
                formula.append([transplants[i][j]], weight=1)

    return formula, {"transplants": transplants}
