# Covering (OPL example): hire a set of workers so that every task has at
# least one hired worker qualified for it, at the least total hiring cost.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def build(instance):
    nb_workers = instance["nb_workers"]
    num_tasks = instance["num_tasks"]
    qualified = instance["Qualified"]  # 1-based worker numbers per task
    cost = instance["Cost"]

    pool = IDPool()
    formula = WCNF()

    # workers[i] is true when worker i is hired.
    workers = [pool.id(("workers", i)) for i in range(nb_workers)]

    # Every task is performed: at least one worker qualified for it is hired.
    for j in range(num_tasks):
        formula.append([workers[c - 1] for c in qualified[j]])

    # total_cost is a declared output: an Integer equal to the hiring cost of
    # the chosen workers. It cannot exceed the cost of hiring everyone, which
    # bounds its domain (the reference's nb_workers * sum(Cost) is looser).
    # The equation is pseudo-Boolean on its order literals, since
    # total_cost = sum over k of [total_cost >= k].
    top = max(sum(cost), 1)
    total_cost = Integer("total_cost", 0, top, encoding="coupled", vpool=pool)
    formula.extend(total_cost.domain_clauses())
    order = [total_cost.ge(k) for k in range(1, top + 1)]
    formula.extend(PBEnc.equals(lits=workers + order,
                                weights=list(cost) + [-1] * top, bound=0,
                                vpool=pool, encoding=EncType.bdd).clauses)

    # Minimise the total cost: hiring worker i pays its cost.
    for i in range(nb_workers):
        if cost[i] > 0:
            formula.append([-workers[i]], weight=cost[i])

    return formula, {"total_cost": total_cost, "workers": workers}
