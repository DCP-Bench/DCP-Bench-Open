# Capital budgeting: choose investments whose cash outflows fit in the budget so that the
# total net present value (NPV) is as large as possible.
# PySAT only decides satisfiability, so the NPV to maximise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it). The total NPV z is that
# objective; it is not modelled as an integer variable, because a variable ranging over
# 0..sum(npv) with thousands of values exhausted the 2048 MB memory limit in attempt-001.
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def build(instance):
    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = len(npv)

    pool = IDPool()
    cnf = CNF()
    # x[i] is true when investment i is chosen
    x = [pool.id(("x", i)) for i in range(n)]

    # the cash outflow of the chosen investments must not exceed the budget
    cnf.extend(PBEnc.leq(lits=x, weights=cash_flow, bound=budget, vpool=pool).clauses)

    return cnf, {"x": x}, ("maximize", x, npv)
