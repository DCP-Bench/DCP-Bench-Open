# SONET ring design (CSPLib 056): place nodes on rings, each placement using
# one add-drop multiplexer (ADM), so that every pair of nodes with traffic
# demand shares a ring and no ring holds more nodes than its capacity, using
# as few ADMs as possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType as PBEncType, PBEnc


def build(instance):
    r = instance["r"]
    n = instance["n"]
    demand = instance["demand"]
    capacity_nodes = instance["capacity_nodes"]

    pool = IDPool()
    formula = WCNF()

    # ring_config[k][i] is true when node i is on ring k.
    ring_config = [[pool.id(("ring_config", k, i)) for i in range(n)]
                   for k in range(r)]

    # Two nodes with demand between them share at least one ring: for some
    # ring k, both are on it. together[k] implies both nodes are on ring k,
    # and one of the together[k] must hold.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                together = []
                for k in range(r):
                    t = pool.id(("together", k, i, j))
                    formula.append([-t, ring_config[k][i]])
                    formula.append([-t, ring_config[k][j]])
                    together.append(t)
                formula.append(together)

    # No ring hosts more nodes than its capacity.
    for k in range(r):
        formula.extend(CardEnc.atmost(lits=ring_config[k], bound=capacity_nodes[k],
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    # total_adms is a declared output: an Integer equal to the number of node
    # placements. Ring k holds at most min(capacity, n) nodes, which bounds
    # its domain. The equation is pseudo-Boolean on its order literals, since
    # total_adms = sum over m of [total_adms >= m].
    placements = [lit for row in ring_config for lit in row]
    top = max(sum(min(max(c, 0), n) for c in capacity_nodes), 1)
    total_adms = Integer("total_adms", 0, top, encoding="coupled", vpool=pool)
    formula.extend(total_adms.domain_clauses())
    order = [total_adms.ge(m) for m in range(1, top + 1)]
    formula.extend(PBEnc.equals(lits=placements + order,
                                weights=[1] * len(placements) + [-1] * top,
                                bound=0, vpool=pool,
                                encoding=PBEncType.bdd).clauses)

    # Minimise the number of ADMs: every node placed on a ring pays 1.
    for lit in placements:
        formula.append([-lit], weight=1)

    return formula, {"ring_config": ring_config, "total_adms": total_adms}
