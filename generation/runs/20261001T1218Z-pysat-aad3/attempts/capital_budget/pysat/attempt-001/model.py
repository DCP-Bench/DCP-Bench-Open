# Capital budgeting: choose investments whose cash outflows fit in the budget so that the
# total net present value (NPV) is as large as possible.
# PySAT only decides satisfiability, so the NPV to maximise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = len(npv)

    pool = IDPool()
    # x[i] = 1 if investment i is chosen
    x = [Integer(f"x{i}", 0, 1, vpool=pool) for i in range(n)]
    # z = total NPV of the chosen investments
    z = Integer("z", 0, sum(npv), encoding="order", vpool=pool)
    engine = IntegerEngine(vars=x + [z], vpool=pool)

    # the cash outflow of the chosen investments must not exceed the budget
    engine.add_linear(sum(cash_flow[i] * x[i] for i in range(n)) <= budget)
    # z is the NPV of the chosen investments
    engine.add_linear(z - sum(npv[i] * x[i] for i in range(n)) == 0)

    return engine.clausify(), {"x": x, "z": z}, ("maximize", z)
